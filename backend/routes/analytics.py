from datetime import datetime, timezone, timedelta
from flask import Blueprint, jsonify, request
from sqlalchemy import func
from backend.models import SessionLocal
from backend.models.issue import Issue, IssueCategory
from backend.models.cluster import IssueCluster
from backend.config import Config

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/v1/analytics")


@analytics_bp.route("/summary", methods=["GET"])
def get_summary():
    """Returns executive civic operations KPIs, status breakdowns, and SLA metrics."""
    db = SessionLocal()
    try:
        total_issues = db.query(Issue).count()
        
        # Status counts
        status_counts = dict(
            db.query(Issue.status, func.count(Issue.id))
            .group_by(Issue.status)
            .all()
        )

        resolved_count = status_counts.get(Issue.STATUS_RESOLVED, 0) + status_counts.get(Issue.STATUS_VERIFIED, 0)
        open_count = total_issues - resolved_count - status_counts.get(Issue.STATUS_REJECTED, 0)

        # Overdue issues (open issues older than SLA target)
        now = datetime.now(timezone.utc)
        ack_sla_limit = now - timedelta(hours=Config.SLA_ACKNOWLEDGE_HOURS)
        res_sla_limit = now - timedelta(hours=Config.SLA_RESOLVE_HOURS)

        unacknowledged_overdue = (
            db.query(Issue)
            .filter(
                Issue.status == Issue.STATUS_SUBMITTED,
                Issue.created_at < ack_sla_limit,
            )
            .count()
        )

        unresolved_overdue = (
            db.query(Issue)
            .filter(
                Issue.status.in_([Issue.STATUS_ASSIGNED, Issue.STATUS_IN_PROGRESS, Issue.STATUS_TRIAGED]),
                Issue.created_at < res_sla_limit,
            )
            .count()
        )

        # Issues by Category
        category_breakdown = (
            db.query(IssueCategory.name, func.count(Issue.id))
            .join(Issue, Issue.category_id == IssueCategory.id)
            .group_by(IssueCategory.name)
            .all()
        )

        # Calculate average acknowledgement and resolution times
        acknowledged_issues = db.query(Issue).filter(Issue.acknowledged_at.isnot(None)).all()
        ack_durations = [
            (i.acknowledged_at - i.created_at).total_seconds() / 3600.0
            for i in acknowledged_issues
            if i.acknowledged_at and i.created_at
        ]
        avg_ack_hours = round(sum(ack_durations) / len(ack_durations), 1) if ack_durations else 0.0

        resolved_issues = db.query(Issue).filter(Issue.resolved_at.isnot(None)).all()
        res_durations = [
            (i.resolved_at - i.created_at).total_seconds() / 3600.0
            for i in resolved_issues
            if i.resolved_at and i.created_at
        ]
        avg_res_hours = round(sum(res_durations) / len(res_durations), 1) if res_durations else 0.0

        active_clusters = db.query(IssueCluster).filter_by(status="active").count()

        return jsonify({
            "is_demo_data": True,
            "total_issues": total_issues,
            "open_issues": open_count,
            "resolved_issues": resolved_count,
            "overdue_issues": unacknowledged_overdue + unresolved_overdue,
            "unacknowledged_overdue": unacknowledged_overdue,
            "unresolved_overdue": unresolved_overdue,
            "active_clusters": active_clusters,
            "avg_acknowledge_hours": avg_ack_hours,
            "avg_resolve_hours": avg_res_hours,
            "status_breakdown": status_counts,
            "category_breakdown": [{"category": name, "count": count} for name, count in category_breakdown],
        })
    finally:
        db.close()


@analytics_bp.route("/hotspots", methods=["GET"])
def get_hotspots():
    """Aggregates infrastructure hotspots grouped by approximate area/district."""
    db = SessionLocal()
    try:
        hotspots = (
            db.query(
                Issue.ward_or_district,
                func.count(Issue.id).label("issue_count"),
                func.avg(Issue.priority_score).label("avg_priority"),
                func.sum(func.case((Issue.safety_hazard == True, 1), else_=0)).label("safety_hazards"),
            )
            .filter(Issue.ward_or_district.isnot(None))
            .group_by(Issue.ward_or_district)
            .order_by(func.count(Issue.id).desc())
            .all()
        )

        results = []
        for ward, count, avg_prio, hazards in hotspots:
            # Find dominant category for this hotspot
            top_cat = (
                db.query(IssueCategory.name, func.count(Issue.id))
                .join(Issue, Issue.category_id == IssueCategory.id)
                .filter(Issue.ward_or_district == ward)
                .group_by(IssueCategory.name)
                .order_by(func.count(Issue.id).desc())
                .first()
            )

            results.append({
                "area": ward or "Unspecified",
                "issue_count": count,
                "avg_priority": round(float(avg_prio or 0), 1),
                "safety_hazards": int(hazards or 0),
                "top_category": top_cat[0] if top_cat else "Various",
            })

        return jsonify(results)
    finally:
        db.close()
