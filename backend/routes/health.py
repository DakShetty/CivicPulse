from datetime import datetime, timezone
from flask import Blueprint, jsonify
from sqlalchemy import text
from backend.models import SessionLocal
from backend.models.audit import AuditEvent
from backend.config import Config
from backend.routes.auth import require_auth

health_bp = Blueprint("health", __name__, url_prefix="/api/v1")


@health_bp.route("/health", methods=["GET"])
def health_check():
    """System health check verifying database and storage connectivity."""
    db_ok = False
    error = None

    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_ok = True
    except Exception as e:
        error = str(e)

    status_code = 200 if db_ok else 503
    return jsonify({
        "status": "healthy" if db_ok else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "connected" if db_ok else f"failed: {error}",
        "storage_driver": Config.STORAGE_DRIVER,
        "queue_driver": Config.QUEUE_DRIVER,
        "notification_driver": Config.NOTIFICATION_DRIVER,
        "environment": Config.ENV,
    }), status_code


@health_bp.route("/audit", methods=["GET"])
@require_auth(roles=["admin"])
def list_audit_events():
    """Lists audit trail entries for administrative compliance."""
    db = SessionLocal()
    try:
        events = db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(50).all()
        return jsonify([e.to_dict() for e in events])
    finally:
        db.close()
