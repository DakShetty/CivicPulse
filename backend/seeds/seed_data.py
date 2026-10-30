import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

project_root = str(Path(__file__).resolve().parent.parent.parent)
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


def seed_database(reset: bool = False):
    """Populates database with categories, roles, and 18+ realistic Indian municipal reports across Bengaluru, Mumbai, and Delhi."""
    init_db(Config.SQLALCHEMY_DATABASE_URI)
    db = SessionLocal()

    try:
        if reset:
            print("Resetting existing issues, clusters, assignments, and audit events for fresh seed...")
            db.query(IssueClusterMember).delete()
            db.query(IssueCluster).delete()
            db.query(Assignment).delete()
            db.query(StatusHistory).delete()
            db.query(AuditEvent).delete()
            db.query(Issue).delete()
            db.commit()

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

        # 2. Seed Default Demo Users if missing
        admin = db.query(User).filter_by(email="admin@civicpulse.org").first()
        if not admin:
            admin = db.query(User).filter_by(email="admin@civicpulse.local").first()
        if not admin:
            print("Seeding default demo users...")
            admin = User(
                display_name="CivicPulse Admin",
                email="admin@civicpulse.org",
                role="admin",
                is_active=True,
            )
            admin.set_password("Admin@123")
            db.add(admin)

        worker = db.query(User).filter_by(email="fieldworker@civicpulse.local").first()
        if not worker:
            worker = User(
                display_name="Carlos Mendez (Field Op)",
                email="fieldworker@civicpulse.local",
                role="field_worker",
                is_active=True,
            )
            worker.set_password("WorkerPass123!")
            db.add(worker)
        else:
            worker.is_active = True

        citizen = db.query(User).filter_by(email="citizen@civicpulse.local").first()
        if not citizen:
            citizen = User(
                display_name="Priya Sharma (Resident)",
                email="citizen@civicpulse.local",
                role="reporter",
                is_active=True,
            )
            citizen.set_password("CitizenPass123!")
            db.add(citizen)

        db.commit()
        db.refresh(admin)
        db.refresh(worker)
        db.refresh(citizen)

        # 3. Seed Sample Issues if empty or reset
        if db.query(Issue).count() == 0 or reset:
            print("Seeding 18+ realistic Indian sample issues across Bengaluru, Mumbai, and Delhi...")
            cats = {c.code: c for c in db.query(IssueCategory).all()}
            now = datetime.now(timezone.utc)

            # Sample issue definitions across major Indian metropolitan hubs
            sample_data = [
                # === BENGALURU (BBMP) ===
                {
                    "title": "Severe dangerous pothole on 100 Feet Road",
                    "description": "Deep dangerous crater in asphalt right before 12th Main junction. Two-wheelers losing balance.",
                    "code": "pothole",
                    "address": "452, 100 Feet Road, Near 12th Main Junction, Indiranagar",
                    "ward": "BBMP East Zone - Indiranagar (Ward 80)",
                    "lat": 12.9719,
                    "lon": 77.6412,
                    "severity": 4,
                    "safety": True,
                    "critical": True,
                    "status": Issue.STATUS_IN_PROGRESS,
                    "age_hours": 36,
                    "worker": worker,
                    "cluster_key": "blr_pothole",
                },
                {
                    "title": "Road cavity and surface subsidence on 100 Feet Road",
                    "description": "Large deep pothole expanding across left lane near Indiranagar 12th Main. Causing severe deceleration.",
                    "code": "pothole",
                    "address": "468, 100 Feet Road, Indiranagar",
                    "ward": "BBMP East Zone - Indiranagar (Ward 80)",
                    "lat": 12.9722,
                    "lon": 77.6415,
                    "severity": 4,
                    "safety": True,
                    "critical": False,
                    "status": Issue.STATUS_SUBMITTED,
                    "age_hours": 12,
                    "cluster_key": "blr_pothole",
                },
                {
                    "title": "BWSSB main potable pipeline leakage flooding street",
                    "description": "High volume potable water gushing from underground pipeline joint onto the main road near Sony World.",
                    "code": "water_leak",
                    "address": "80 Feet Road, Near Sony World Signal, Koramangala 4th Block",
                    "ward": "BBMP South Zone - Koramangala (Ward 151)",
                    "lat": 12.9352,
                    "lon": 77.6245,
                    "severity": 5,
                    "safety": False,
                    "critical": True,
                    "status": Issue.STATUS_ASSIGNED,
                    "age_hours": 18,
                    "worker": worker,
                },
                {
                    "title": "Streetlight pole flickering and completely dark at night",
                    "description": "Municipal street lights out for over 300 meters near Metro station, creating safety risk for pedestrians.",
                    "code": "streetlight",
                    "address": "MG Road, Opposite Trinity Metro Station",
                    "ward": "BBMP Central Zone - Ward 111 (Shantala Nagar)",
                    "lat": 12.9728,
                    "lon": 77.6169,
                    "severity": 3,
                    "safety": True,
                    "critical": False,
                    "status": Issue.STATUS_RESOLVED,
                    "age_hours": 80,
                    "resolved_hours_ago": 6,
                    "worker": worker,
                },
                {
                    "title": "Severe monsoon waterlogging and blocked storm drain",
                    "description": "Stormwater drain choked with plastic debris; knee-deep rainwater causing 2km vehicle gridlock.",
                    "code": "drainage",
                    "address": "Hosur Road - Outer Ring Road Junction, Silk Board",
                    "ward": "BBMP South Zone - HSR Layout (Ward 174)",
                    "lat": 12.9172,
                    "lon": 77.6228,
                    "severity": 5,
                    "safety": True,
                    "critical": True,
                    "status": Issue.STATUS_TRIAGED,
                    "age_hours": 28,
                },
                {
                    "title": "Uncollected municipal garbage waste overflow on footpath",
                    "description": "Piles of domestic solid waste not cleared for 4 days. Foul odor and stray dog menace on public sidewalk.",
                    "code": "waste",
                    "address": "ITPL Main Road, Near Hope Farm Signal, Whitefield",
                    "ward": "BBMP Mahadevapura - Whitefield (Ward 84)",
                    "lat": 12.9854,
                    "lon": 77.7314,
                    "severity": 3,
                    "safety": False,
                    "critical": False,
                    "status": Issue.STATUS_SUBMITTED,
                    "age_hours": 10,
                },
                {
                    "title": "Broken pedestrian footpath tiles and open utility slab",
                    "description": "Concrete footpath slabs displaced by tree roots leaving a 3-foot ditch hazard for senior citizens.",
                    "code": "footpath",
                    "address": "9th Main Road, Near 4th Block Complex, Jayanagar",
                    "ward": "BBMP South Zone - Jayanagar (Ward 153)",
                    "lat": 12.9308,
                    "lon": 77.5838,
                    "severity": 2,
                    "safety": False,
                    "critical": False,
                    "status": Issue.STATUS_VERIFIED,
                    "age_hours": 120,
                    "resolved_hours_ago": 24,
                },
                {
                    "title": "Vandalized bus shelter with hanging damaged tin sheet",
                    "description": "Roof metal sheet dangling dangerously over commuter bench. Risk of falling during heavy wind.",
                    "code": "facility",
                    "address": "Sampige Road, 8th Cross Bus Stop, Malleshwaram",
                    "ward": "BBMP West Zone - Malleshwaram (Ward 65)",
                    "lat": 13.0031,
                    "lon": 77.5702,
                    "severity": 4,
                    "safety": True,
                    "critical": False,
                    "status": Issue.STATUS_SUBMITTED,
                    "age_hours": 16,
                },

                # === MUMBAI (BMC) ===
                {
                    "title": "Deep asphalt trench and road collapse on Linking Road",
                    "description": "Underground cable excavation left unpaved on main commercial road. Causes severe traffic snarls and bike accidents.",
                    "code": "pothole",
                    "address": "Linking Road, Near KFC & Khar Telephone Exchange, Bandra West",
                    "ward": "BMC Zone III - Bandra West / Khar (H/West Ward)",
                    "lat": 19.0607,
                    "lon": 72.8335,
                    "severity": 4,
                    "safety": True,
                    "critical": True,
                    "status": Issue.STATUS_IN_PROGRESS,
                    "age_hours": 42,
                    "worker": worker,
                    "cluster_key": "mumbai_linking_rd",
                },
                {
                    "title": "Damaged asphalt depression and road cavity near Linking Road",
                    "description": "Repeated depression in left carriageway just past KFC on Linking Road. Vehicles swerving sharply into oncoming lanes.",
                    "code": "pothole",
                    "address": "Opposite National College, Linking Road, Bandra West",
                    "ward": "BMC Zone III - Bandra West (H/West Ward)",
                    "lat": 19.0614,
                    "lon": 72.8341,
                    "severity": 4,
                    "safety": True,
                    "critical": False,
                    "status": Issue.STATUS_SUBMITTED,
                    "age_hours": 14,
                    "cluster_key": "mumbai_linking_rd",
                },
                {
                    "title": "Subway chronic monsoon flooding & drainage pump breakdown",
                    "description": "Storm drain pump non-functional at Andheri Subway. Water level rising above 2.5 feet, subway blocked for vehicular transit.",
                    "code": "drainage",
                    "address": "Andheri Subway, S.V. Road Connection, Andheri West",
                    "ward": "BMC Zone IV - Andheri West (K/West Ward)",
                    "lat": 19.1197,
                    "lon": 72.8468,
                    "severity": 5,
                    "safety": True,
                    "critical": True,
                    "status": Issue.STATUS_ASSIGNED,
                    "age_hours": 20,
                    "worker": worker,
                },
                {
                    "title": "Displaced promenade pavers & cracked sea barrier railing",
                    "description": "Monsoon high tide damaged pedestrian pavers and cast-iron safety fence along the public promenade.",
                    "code": "footpath",
                    "address": "Marine Drive Promenade, Near Air India Building, Nariman Point",
                    "ward": "BMC Zone I - South Mumbai (A Ward)",
                    "lat": 18.9288,
                    "lon": 72.8228,
                    "severity": 3,
                    "safety": False,
                    "critical": True,
                    "status": Issue.STATUS_TRIAGED,
                    "age_hours": 50,
                },
                {
                    "title": "Massive uncollected vegetable & commercial refuse overflow",
                    "description": "Multiple community garbage bins overflowing across the intersection. Severe odor and pedestrian obstruction.",
                    "code": "waste",
                    "address": "Dadar TT Circle, Near Phool Galli & Station Road, Dadar",
                    "ward": "BMC Zone II - Dadar / Matunga (F/North Ward)",
                    "lat": 19.0178,
                    "lon": 72.8478,
                    "severity": 4,
                    "safety": False,
                    "critical": False,
                    "status": Issue.STATUS_IN_PROGRESS,
                    "age_hours": 26,
                    "worker": worker,
                },
                {
                    "title": "High-mast lighting fixture broken and dark pedestrian crossing",
                    "description": "High-mast tower lights dead near shopping complex roundabout, creating a complete blind spot for crossing pedestrians.",
                    "code": "streetlight",
                    "address": "Central Avenue, Near Galleria Mall, Hiranandani Gardens, Powai",
                    "ward": "BMC Zone VI - Powai / Kanjurmarg (S Ward)",
                    "lat": 19.1176,
                    "lon": 72.9060,
                    "severity": 2,
                    "safety": True,
                    "critical": False,
                    "status": Issue.STATUS_RESOLVED,
                    "age_hours": 72,
                    "resolved_hours_ago": 12,
                    "worker": worker,
                },

                # === DELHI / NCR (MCD) ===
                {
                    "title": "DJB potable main pipe rupture flooding commercial corridor",
                    "description": "High pressure potable water bursting from cracked junction box. Submerging inner circular road and shopfront steps.",
                    "code": "water_leak",
                    "address": "Inner Circle, Block C & D, Connaught Place",
                    "ward": "NDMC Central Zone - Connaught Place",
                    "lat": 28.6328,
                    "lon": 77.2197,
                    "severity": 5,
                    "safety": True,
                    "critical": True,
                    "status": Issue.STATUS_IN_PROGRESS,
                    "age_hours": 30,
                    "worker": worker,
                },
                {
                    "title": "Displaced heavy stone walkway slabs and missing drain cover",
                    "description": "Broken sidewalk stones right outside heritage village gate. Pedestrians stepping onto open 4-foot deep storm sewer.",
                    "code": "footpath",
                    "address": "Hauz Khas Village Road, Near Deer Park Gate, South Delhi",
                    "ward": "MCD South Zone - Hauz Khas / Green Park",
                    "lat": 28.5535,
                    "lon": 77.2001,
                    "severity": 4,
                    "safety": True,
                    "critical": False,
                    "status": Issue.STATUS_ASSIGNED,
                    "age_hours": 15,
                    "worker": worker,
                },
                {
                    "title": "Dead commercial streetlights on Ajmal Khan Road",
                    "description": "Over 8 heritage municipal light fixtures flickering and dead, leaving busy market corridor in total darkness.",
                    "code": "streetlight",
                    "address": "Ajmal Khan Road Market, Near Metro Gate 3, Karol Bagh",
                    "ward": "MCD Karol Bagh Zone - Ward 88",
                    "lat": 28.6517,
                    "lon": 77.1906,
                    "severity": 3,
                    "safety": True,
                    "critical": False,
                    "status": Issue.STATUS_SUBMITTED,
                    "age_hours": 8,
                },
                {
                    "title": "Choked municipal stormwater culvert flooding central avenue",
                    "description": "Heavy debris and shopping packaging chokes drainage culvert during rain, backflowing muddy water onto shops.",
                    "code": "drainage",
                    "address": "Central Market, Feroze Gandhi Road, Lajpat Nagar II",
                    "ward": "MCD Central Zone - Lajpat Nagar",
                    "lat": 28.5677,
                    "lon": 77.2433,
                    "severity": 4,
                    "safety": False,
                    "critical": True,
                    "status": Issue.STATUS_TRIAGED,
                    "age_hours": 22,
                },
            ]

            created_issues = []
            cluster_dict = {}

            for item in sample_data:
                category = cats[item["code"]]
                created_dt = now - timedelta(hours=item["age_hours"])
                score, expl = calculate_priority_score(
                    severity=item["severity"],
                    safety_hazard=item["safety"],
                    impacts_critical_infrastructure=item["critical"],
                    cluster_member_count=2 if item.get("cluster_key") else 1,
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

                # Track cluster groups
                ckey = item.get("cluster_key")
                if ckey:
                    if ckey not in cluster_dict:
                        cluster_dict[ckey] = []
                    cluster_dict[ckey].append(issue)

                # Assignment
                if item.get("worker"):
                    assign = Assignment(
                        issue_id=issue.id,
                        field_worker_id=item["worker"].id,
                        assigned_by_id=admin.id,
                        notes="Dispatched per municipal zonal roster. High-priority public report.",
                        created_at=issue.assigned_at or now,
                    )
                    db.add(assign)

                # Status History
                db.add(StatusHistory(
                    issue_id=issue.id,
                    old_status=None,
                    new_status=Issue.STATUS_SUBMITTED,
                    actor_id=citizen.id,
                    note="Initial citizen report submitted via portal.",
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

            # Duplicate Clusters:
            # 1. Bengaluru Indiranagar Pothole Cluster
            if "blr_pothole" in cluster_dict and len(cluster_dict["blr_pothole"]) >= 2:
                c1_lead = cluster_dict["blr_pothole"][0]
                c1_dup = cluster_dict["blr_pothole"][1]

                cluster1 = IssueCluster(
                    title="100 Feet Road Pothole Cluster (BBMP Indiranagar)",
                    representative_issue_id=c1_lead.id,
                    status="active",
                    created_at=now - timedelta(hours=10),
                )
                db.add(cluster1)
                db.flush()

                c1_lead.cluster_id = cluster1.id
                c1_lead.is_cluster_representative = True
                c1_dup.cluster_id = cluster1.id

                db.add(IssueClusterMember(
                    cluster_id=cluster1.id,
                    issue_id=c1_dup.id,
                    similarity_score=0.91,
                    distance_km=0.035,
                    text_similarity=0.78,
                    similarity_explanation="Located 35m apart; Same category (Pothole); 78% text similarity. Composite score: 91%",
                    reviewed_status="pending_review",
                    created_at=now - timedelta(hours=10),
                ))

            # 2. Mumbai Linking Road Pothole Cluster
            if "mumbai_linking_rd" in cluster_dict and len(cluster_dict["mumbai_linking_rd"]) >= 2:
                c2_lead = cluster_dict["mumbai_linking_rd"][0]
                c2_dup = cluster_dict["mumbai_linking_rd"][1]

                cluster2 = IssueCluster(
                    title="Linking Road Asphalt Cavity Cluster (BMC Bandra West)",
                    representative_issue_id=c2_lead.id,
                    status="active",
                    created_at=now - timedelta(hours=8),
                )
                db.add(cluster2)
                db.flush()

                c2_lead.cluster_id = cluster2.id
                c2_lead.is_cluster_representative = True
                c2_dup.cluster_id = cluster2.id

                db.add(IssueClusterMember(
                    cluster_id=cluster2.id,
                    issue_id=c2_dup.id,
                    similarity_score=0.89,
                    distance_km=0.082,
                    text_similarity=0.74,
                    similarity_explanation="Located 82m apart; Same category (Pothole); 74% text similarity on Linking Road corridor. Composite score: 89%",
                    reviewed_status="pending_review",
                    created_at=now - timedelta(hours=8),
                ))

            # Seed sample operations & compliance report records
            from backend.models.issue import ReportRecord
            if db.query(ReportRecord).count() == 0:
                rep1 = ReportRecord(
                    title="Quarterly Municipal Operations & SLA Audit (Q3)",
                    report_type="summary_pdf",
                    requested_by_id=admin.id,
                    s3_object_key="reports/summary_q3_audit.pdf",
                    file_size_bytes=425100,
                    status="completed",
                    created_at=now - timedelta(days=2),
                )
                rep2 = ReportRecord(
                    title="All India Municipal Infrastructure Issues Raw Export (CSV)",
                    report_type="summary_csv",
                    requested_by_id=admin.id,
                    s3_object_key="reports/issues_export_raw.csv",
                    file_size_bytes=18450,
                    status="completed",
                    created_at=now - timedelta(days=1),
                )
                db.add_all([rep1, rep2])

            db.commit()
            print(f"Database successfully populated with {len(sample_data)} Indian issues across Bengaluru, Mumbai, and Delhi!")

    finally:
        db.close()


if __name__ == "__main__":
    do_reset = "--reset" in sys.argv
    seed_database(reset=do_reset)
