import json
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, g
from backend.models import SessionLocal
from backend.models.cluster import IssueCluster, IssueClusterMember
from backend.models.issue import Issue
from backend.models.audit import AuditEvent
from backend.services.priority_scorer import calculate_priority_score
from backend.routes.auth import require_auth

clusters_bp = Blueprint("clusters", __name__, url_prefix="/api/v1/clusters")


@clusters_bp.route("", methods=["GET"])
def list_clusters():
    """Lists all duplicate clusters with members and similarity explanations."""
    db = SessionLocal()
    try:
        clusters = db.query(IssueCluster).order_by(IssueCluster.created_at.desc()).all()
        return jsonify([c.to_dict() for c in clusters])
    finally:
        db.close()


@clusters_bp.route("/<int:cluster_id>", methods=["GET"])
def get_cluster(cluster_id: int):
    """Retrieves cluster details including representative issue and member reports."""
    db = SessionLocal()
    try:
        cluster = db.query(IssueCluster).filter_by(id=cluster_id).first()
        if not cluster:
            return jsonify({"error": "Cluster not found"}), 404

        data = cluster.to_dict()
        rep_issue = db.query(Issue).filter_by(id=cluster.representative_issue_id).first()
        data["representative_issue"] = rep_issue.to_dict() if rep_issue else None
        return jsonify(data)
    finally:
        db.close()


@clusters_bp.route("/members/<int:member_id>/review", methods=["POST"])
@require_auth(roles=["admin"])
def review_member(member_id: int):
    """Admin reviews a duplicate suggestion: 'confirmed', 'separated', or 'dismissed'.
    As specified in Section 4.3: Original records are preserved and never deleted.
    """
    data = request.get_json() or {}
    action = data.get("action")  # 'confirmed', 'separated', 'dismissed'
    notes = data.get("notes", "").strip()

    if action not in ("confirmed", "separated", "dismissed"):
        return jsonify({"error": "Invalid action. Must be 'confirmed', 'separated', or 'dismissed'."}), 400

    db = SessionLocal()
    try:
        member = db.query(IssueClusterMember).filter_by(id=member_id).first()
        if not member:
            return jsonify({"error": "Cluster member link not found"}), 404

        member.reviewed_status = action
        member.reviewed_by_id = g.current_user.id
        member.reviewed_at = datetime.now(timezone.utc)

        issue = db.query(Issue).filter_by(id=member.issue_id).first()

        if action == "separated":
            # Remove from cluster
            if issue:
                issue.cluster_id = None
                issue.is_cluster_representative = False
                # Recalculate priority without cluster boost
                score, expl = calculate_priority_score(
                    severity=issue.severity,
                    safety_hazard=issue.safety_hazard,
                    impacts_critical_infrastructure=issue.impacts_critical_infrastructure,
                    cluster_member_count=1,
                    hours_unresolved=0.0,
                    category_weight=issue.category.default_severity_weight if issue.category else 1.0,
                )
                issue.priority_score = score
                issue.priority_explanation = expl

        # Audit review action
        audit = AuditEvent(
            actor_id=g.current_user.id,
            action=f"CLUSTER_REVIEW_{action.upper()}",
            entity_type="cluster_member",
            entity_id=str(member.id),
            metadata_json=json.dumps({"action": action, "notes": notes, "cluster_id": member.cluster_id}),
            ip_address=request.remote_addr,
        )
        db.add(audit)

        db.commit()
        return jsonify({
            "message": f"Suggestion reviewed as {action}",
            "member": member.to_dict(),
        })
    finally:
        db.close()
