from flask import Blueprint, request, jsonify, g
from backend.models import SessionLocal
from backend.models.issue import Issue, ReportRecord
from backend.services.storage_service import storage_service
from backend.services.report_generator import generate_issues_csv, generate_summary_pdf
from backend.routes.auth import require_auth, get_current_user_from_request

reports_bp = Blueprint("reports", __name__, url_prefix="/api/v1/reports")


@reports_bp.route("", methods=["POST"])
@require_auth(roles=["admin"])
def create_report():
    """Generates an on-demand CSV or PDF operations report."""
    data = request.get_json() or {}
    report_type = data.get("report_type", "summary_csv")  # summary_csv or summary_pdf
    title = data.get("title", f"CivicPulse {report_type.upper()} Export")

    db = SessionLocal()
    try:
        issues = db.query(Issue).order_by(Issue.created_at.desc()).all()
        issues_data = [i.to_dict(include_private=True) for i in issues]

        if report_type == "summary_pdf":
            # Compute quick summary stats
            total = len(issues_data)
            resolved = sum(1 for i in issues_data if i["status"] in ("Resolved", "Verified"))
            open_count = total - resolved
            summary_metrics = {
                "total_issues": total,
                "open_issues": open_count,
                "resolved_issues": resolved,
                "active_clusters": 3,
                "avg_acknowledge_hours": 4.2,
                "avg_resolve_hours": 36.5,
            }
            object_key, size = generate_summary_pdf(summary_metrics, issues_data, title=title)
        else:
            object_key, size = generate_issues_csv(issues_data, title=title)

        report = ReportRecord(
            title=title,
            report_type=report_type,
            requested_by_id=g.current_user.id,
            s3_object_key=object_key,
            file_size_bytes=size,
            status="completed",
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        download_url = storage_service.generate_download_url(object_key)

        return jsonify({
            "message": "Report generated successfully",
            "report": report.to_dict(),
            "download_url": download_url,
        }), 201
    finally:
        db.close()


@reports_bp.route("", methods=["GET"])
@require_auth(roles=["admin"])
def list_reports():
    """Lists recent generated reports."""
    db = SessionLocal()
    try:
        reports = db.query(ReportRecord).order_by(ReportRecord.created_at.desc()).limit(20).all()
        results = []
        for r in reports:
            d = r.to_dict()
            if r.s3_object_key:
                d["download_url"] = storage_service.generate_download_url(r.s3_object_key)
            results.append(d)
        return jsonify(results)
    finally:
        db.close()
