import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.models import init_db, SessionLocal
from backend.models.user import User
from backend.models.issue import (
    IssueCategory,
    Issue,
    StatusHistory,
    generate_public_reference,
)
from backend.models.cluster import IssueCluster, IssueClusterMember
from backend.models.assignment import Assignment
from backend.models.audit import AuditEvent
from backend.services.priority_scorer import calculate_priority_score
from backend.config import Config


def seed_database():
    """Populates database with categories, roles, sample reports, and duplicate clusters."""
    init_db(Config.SQLALCHEMY_DATABASE_URI)
    db = SessionLocal()

    try:
        # 1. Seed Categories if empty
        if db.query(IssueCategory).count() == 0:
            print("Seeding issue categories...")
            categories = [
                IssueCategory(
                    name="Pothole / Road Damage",
                    code="pothole",
                    description="Potholes, cracks, surface erosion, and asphalt subsidence affecting vehicular traffic.",
                    default_severity_weight=1.2,
                    sla_hours=48,
                ),
                IssueCategory(
                    name="Broken Streetlight",
                    code="streetlight",
                    description="Out-of-service, flickering, or damaged light poles causing dark pedestrian areas.",
                    default_severity_weight=1.0,
                    sla_hours=72,
                ),
                IssueCategory(
                    name="Water Leakage",
                    code="water_leak",
                    description="Burst pipes, main supply leakages, or continuous water wastage on roads.",
                    default_severity_weight=1.3,
                    sla_hours=24,
                ),
                IssueCategory(
                    name="Drainage / Flooding",
                    code="drainage",
                    description="Blocked culverts, overflowing storm drains, or monsoon waterlogging.",
                    default_severity_weight=1.4,
                    sla_hours=24,
                ),
                IssueCategory(
                    name="Waste Overflow",
                    code="waste",
                    description="Uncollected municipal trash bins, illegal debris dumping, or hazardous garbage.",
                    default_severity_weight=0.9,
                    sla_hours=48,
                ),
                IssueCategory(
                    name="Damaged Footpath",
                    code="footpath",
                    description="Broken sidewalk slabs, missing paver blocks, or trip hazards for pedestrians.",
                    default_severity_weight=0.8,
                    sla_hours=96,
                ),
                IssueCategory(
                    name="Public Facility Damage",
                    code="facility",
                    description="Vandalized bus shelters, broken park railings, or damaged public restrooms.",
                    default_severity_weight=0.9,
                    sla_hours=96,
                ),
                IssueCategory(
                    name="Other Infrastructure Issue",
                    code="other",
                    description="General municipal infrastructure defects not covered in standard categories.",
                    default_severity_weight=1.0,
                    sla_hours=72,
                ),
            ]
            db.add_all(categories)
            db.commit()

        # 2. Seed Default Demo Users
        admin = db.query(User).filter_by(email="admin@civicpulse.local").first()
        if not admin:
            print("Seeding default demo users...")
            admin = User(
                display_name="Sarah Jenkins (Admin)",
                email="admin@civicpulse.local",
                role="admin",
                is_active=True,
            )
            admin.set_password("AdminPass123!")

            worker = User(
                display_name="Carlos Mendez (Field Op)",
                email="fieldworker@civicpulse.local",
                role="field_worker",
                is_active=True,
            )
            worker.set_password("WorkerPass123!")

            citizen = User(
                display_name="Priya Sharma (Resident)",
                email="citizen@civicpulse.local",
                role="reporter",
                is_active=True,
            )
            citizen.set_password("CitizenPass123!")

            db.add_all([admin, worker, citizen])
            db.commit()
            db.refresh(admin)
            db.refresh(worker)
            db.refresh(citizen)
        else:
            worker = db.query(User).filter_by(email="fieldworker@civicpulse.local").first()
            citizen = db.query(User).filter_by(email="citizen@civicpulse.local").first()

        # 3. Seed Sample Issues if empty
        if db.query(Issue).count() == 0:
            print("Seeding realistic sample issues and duplicate clusters...")
            cats = {c.code: c for c in db.query(IssueCategory).all()}
            now = datetime.now(timezone.utc)

            # Sample issue definitions around a central metropolitan area
            # Base coords: Downtown Central ~ lat 37.7749, lon -122.4194
            sample_data = [
                {
                    "title": "Deep dangerous pothole near 5th cross road",
                    "description": "Large deep pothole spanning right lane. Causing tires to burst and severe deceleration.",
                    "code": "pothole",
                    "address": "452 Market St, Near 5th Cross",
                    "ward": "Downtown Central",
                    "lat": 37.7752,
                    "lon": -122.4189,
                    "severity": 4,
                    "safety": True,
                    "critical": True,
                    "status": Issue.STATUS_IN_PROGRESS,
                    "age_hours": 36,
                    "worker": worker,
                },
                {
                    "title": "Severe road cavity on Market Street",
                    "description": "Deep pothole in the asphalt near 5th intersection. Hazardous to two-wheelers.",
                    "code": "pothole",
                    "address": "460 Market St",
                    "ward": "Downtown Central",
                    "lat": 37.7754,
                    "lon": -122.4187,
                    "severity": 4,
                    "safety": True,
                    "critical": False,
                    "status": Issue.STATUS_SUBMITTED,
                    "age_hours": 12,
                    "is_duplicate_of_first": True,
                },
                {
                    "title": "High pressure water pipe leaking on sidewalk",
                    "description": "Clean potable water spewing continuously from municipal pipe onto road.",
                    "code": "water_leak",
                    "address": "120 Riverside Ave",
                    "ward": "Riverside Ward",
                    "lat": 37.7831,
                    "lon": -122.4042,
                    "severity": 5,
                    "safety": False,
                    "critical": True,
                    "status": Issue.STATUS_ASSIGNED,
                    "age_hours": 18,
                    "worker": worker,
                },
                {
                    "title": "Streetlight pole flickering and unlit for 3 nights",
                    "description": "Dark stretch of pavement creating unsafe walking condition for night commuters.",
                    "code": "streetlight",
                    "address": "88 Pine Tree Blvd",
                    "ward": "Hillside Suburb",
                    "lat": 37.7690,
                    "lon": -122.4460,
                    "severity": 3,
                    "safety": True,
                    "critical": False,
                    "status": Issue.STATUS_RESOLVED,
                    "age_hours": 80,
                    "resolved_hours_ago": 6,
                    "worker": worker,
                },
                {
                    "title": "Storm drain clogged with leaves and plastic debris",
                    "description": "Water logging up to 8 inches after light drizzle. Mosquito breeding risk.",
                    "code": "drainage",
                    "address": "304 Innovation Way",
                    "ward": "Tech District",
                    "lat": 37.7895,
                    "lon": -122.3990,
                    "severity": 4,
                    "safety": False,
                    "critical": True,
                    "status": Issue.STATUS_TRIAGED,
                    "age_hours": 28,
                },
                {
                    "title": "Public trash dumpster overflowing onto pedestrian walk",
                    "description": "Garbage has not been collected since Friday. Strong odor and rodents reported.",
                    "code": "waste",
                    "address": "77 Civic Square",
                    "ward": "Downtown Central",
                    "lat": 37.7770,
                    "lon": -122.4170,
                    "severity": 3,
                    "safety": False,
                    "critical": False,
                    "status": Issue.STATUS_SUBMITTED,
                    "age_hours": 10,
                },
                {
                    "title": "Cracked concrete sidewalk pavers causing tripping",
                    "description": "Slabs raised by tree roots; elderly pedestrians having difficulty walking.",
                    "code": "footpath",
                    "address": "210 Oak Ridge Dr",
                    "ward": "Hillside Suburb",
                    "lat": 37.7665,
                    "lon": -122.4490,
                    "severity": 2,
                    "safety": False,
                    "critical": False,
                    "status": Issue.STATUS_VERIFIED,
                    "age_hours": 120,
                    "resolved_hours_ago": 24,
                },
            ]

            created_issues = []
            for item in sample_data:
                category = cats[item["code"]]
                created_dt = now - timedelta(hours=item["age_hours"])
                score, expl = calculate_priority_score(
                    severity=item["severity"],
                    safety_hazard=item["safety"],
                    impacts_critical_infrastructure=item["critical"],
                    cluster_member_count=2 if item.get("is_duplicate_of_first") else 1,
                    hours_unresolved=item["age_hours"] if item["status"] != Issue.STATUS_RESOLVED else 0,
                    category_weight=category.default_severity_weight,
                )

                issue = Issue(
                    public_reference=generate_public_reference(),
                    reporter_id=citizen.id,
                    category_id=category.id,
                    title=item["title"],
                    description=item["description"],
                    approximate_address=item["address"],
                    ward_or_district=item["ward"],
                    latitude=item["lat"],
                    longitude=item["lon"],
                    severity=item["severity"],
                    safety_hazard=item["safety"],
                    impacts_critical_infrastructure=item["critical"],
                    priority_score=score,
                    priority_explanation=expl,
                    status=item["status"],
                    created_at=created_dt,
                    acknowledged_at=created_dt + timedelta(hours=2) if item["status"] != Issue.STATUS_SUBMITTED else None,
                    assigned_at=created_dt + timedelta(hours=4) if item.get("worker") else None,
                    resolved_at=now - timedelta(hours=item.get("resolved_hours_ago", 0)) if item["status"] in (Issue.STATUS_RESOLVED, Issue.STATUS_VERIFIED) else None,
                    verified_at=now - timedelta(hours=item.get("resolved_hours_ago", 0)) if item["status"] == Issue.STATUS_VERIFIED else None,
                )
                db.add(issue)
                db.flush()
                created_issues.append((issue, item))

                # Assignment
                if item.get("worker"):
                    assign = Assignment(
                        issue_id=issue.id,
                        field_worker_id=item["worker"].id,
                        assigned_by_id=admin.id,
                        notes="Dispatched per morning priority roster.",
                        created_at=issue.assigned_at or now,
                    )
                    db.add(assign)

                # Status History
                db.add(StatusHistory(
                    issue_id=issue.id,
                    old_status=None,
                    new_status=Issue.STATUS_SUBMITTED,
                    actor_id=citizen.id,
                    note="Initial report submitted.",
                    created_at=created_dt,
                ))

                if item["status"] != Issue.STATUS_SUBMITTED:
                    db.add(StatusHistory(
                        issue_id=issue.id,
                        old_status=Issue.STATUS_SUBMITTED,
                        new_status=item["status"],
                        actor_id=admin.id,
                        note=f"Triage and workflow update to {item['status']}.",
                        created_at=created_dt + timedelta(hours=2),
                    ))

            # Create an explicit sample duplicate cluster linking Issue 0 and Issue 1
            first_issue = created_issues[0][0]
            second_issue = created_issues[1][0]

            cluster = IssueCluster(
                title="Market St Pothole Cluster",
                representative_issue_id=first_issue.id,
                status="active",
                created_at=now - timedelta(hours=10),
            )
            db.add(cluster)
            db.flush()

            first_issue.cluster_id = cluster.id
            first_issue.is_cluster_representative = True
            second_issue.cluster_id = cluster.id

            member_link = IssueClusterMember(
                cluster_id=cluster.id,
                issue_id=second_issue.id,
                similarity_score=0.88,
                distance_km=0.035,
                text_similarity=0.74,
                similarity_explanation="Located 35m apart; Same category (Pothole); 74% text similarity. Composite score: 88%",
                reviewed_status="pending_review",
                created_at=now - timedelta(hours=10),
            )
            db.add(member_link)

            # Audit event
            db.add(AuditEvent(
                actor_id=admin.id,
                action="SYSTEM_SEEDED",
                entity_type="system",
                entity_id="init",
                metadata_json='{"seeded_records": 7, "note": "Classroom demo dataset populated"}',
            ))

            db.commit()
            print("Database successfully seeded with categories, users, sample issues, and duplicate clusters!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
