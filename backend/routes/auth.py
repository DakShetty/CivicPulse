from datetime import datetime, timezone, timedelta
from functools import wraps
import jwt
from flask import Blueprint, request, jsonify, g
from backend.config import Config
from backend.models import SessionLocal
from backend.models.user import User
from backend.models.audit import AuditEvent

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


def generate_token(user: User) -> str:
    """Generates a secure HS256 JWT token for the authenticated user."""
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "display_name": user.display_name,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict | None:
    """Decodes and validates a JWT token."""
    try:
        return jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
    except Exception:
        return None


def get_current_user_from_request():
    """Extracts authenticated user from Authorization header if present."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1].strip()
    payload = decode_token(token)
    if not payload or not payload.get("sub"):
        return None
    db = SessionLocal()
    try:
        user_id = int(payload["sub"])
        return db.query(User).filter_by(id=user_id, is_active=True).first()
    except (ValueError, TypeError):
        return None
    finally:
        db.close()


def require_auth(roles: list[str] | None = None):
    """Decorator to enforce authentication and optional role restrictions."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = get_current_user_from_request()
            if not user:
                return jsonify({"error": "Authentication required. Please provide a valid Bearer token."}), 401
            if roles and user.role not in roles:
                return jsonify({"error": f"Forbidden. Role '{user.role}' lacks permission for this action."}), 403
            g.current_user = user
            return f(*args, **kwargs)
        return wrapper
    return decorator


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    db = SessionLocal()
    try:
        user = db.query(User).filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({"error": "Invalid email or password."}), 401

        if not user.is_active:
            if user.role == "field_worker":
                return jsonify({"error": "Worker account is pending approval by an administrator. Please check back once approved."}), 403
            return jsonify({"error": "Account is inactive. Contact an administrator."}), 403

        token = generate_token(user)

        # Audit login
        audit = AuditEvent(
            actor_id=user.id,
            action="USER_LOGIN",
            entity_type="user",
            entity_id=str(user.id),
            ip_address=request.remote_addr,
        )
        db.add(audit)
        db.commit()

        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": user.to_dict(include_private=True),
        })
    finally:
        db.close()


@auth_bp.route("/register", methods=["POST"])
def register():
    """User and Worker self-registration. Admin creation forbidden here."""
    data = request.get_json() or {}
    display_name = data.get("display_name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    requested_role = (data.get("role") or "reporter").strip().lower()

    if not display_name or not email or not password:
        return jsonify({"error": "Display name, email, and password are required."}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    if requested_role == "admin":
        return jsonify({"error": "Administrator accounts cannot be self-registered. They can only be created by an existing administrator."}), 403

    if requested_role not in ("reporter", "field_worker"):
        return jsonify({"error": "Invalid role. Only 'reporter' and 'field_worker' can register."}), 400

    db = SessionLocal()
    try:
        existing = db.query(User).filter_by(email=email).first()
        if existing:
            return jsonify({"error": "An account with this email already exists."}), 409

        # Workers require Admin approval before activation
        is_worker = (requested_role == "field_worker")
        is_active = not is_worker  # True for reporters, False for field_workers

        new_user = User(
            display_name=display_name,
            email=email,
            role=requested_role,
            is_active=is_active,
        )
        new_user.set_password(password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Audit registration
        audit = AuditEvent(
            actor_id=new_user.id,
            action="WORKER_REGISTER_PENDING" if is_worker else "USER_REGISTER",
            entity_type="user",
            entity_id=str(new_user.id),
            ip_address=request.remote_addr,
        )
        db.add(audit)
        db.commit()

        if is_worker:
            return jsonify({
                "message": "Worker account registered successfully! It is pending administrator approval before you can log in.",
                "pending_approval": True,
                "user": new_user.to_dict(include_private=True),
            }), 201

        token = generate_token(new_user)
        return jsonify({
            "message": "Account created successfully",
            "token": token,
            "user": new_user.to_dict(include_private=True),
        }), 201
    finally:
        db.close()


@auth_bp.route("/me", methods=["GET"])
def me():
    user = get_current_user_from_request()
    if not user:
        return jsonify({"error": "Unauthenticated"}), 401
    return jsonify({"user": user.to_dict(include_private=True)})


@auth_bp.route("/workers/pending", methods=["GET"])
@require_auth(roles=["admin"])
def list_pending_workers():
    """Lists field workers awaiting administrator approval."""
    db = SessionLocal()
    try:
        pending = (
            db.query(User)
            .filter_by(role="field_worker", is_active=False)
            .order_by(User.created_at.desc())
            .all()
        )
        return jsonify([w.to_dict(include_private=True) for w in pending])
    finally:
        db.close()


@auth_bp.route("/workers", methods=["GET"])
@require_auth(roles=["admin"])
def list_all_workers():
    """Lists all field workers (both approved and pending)."""
    db = SessionLocal()
    try:
        workers = (
            db.query(User)
            .filter_by(role="field_worker")
            .order_by(User.created_at.desc())
            .all()
        )
        return jsonify([w.to_dict(include_private=True) for w in workers])
    finally:
        db.close()


@auth_bp.route("/workers/<int:user_id>/approve", methods=["POST"])
@require_auth(roles=["admin"])
def approve_worker(user_id: int):
    """Administrator approves a pending field worker."""
    db = SessionLocal()
    try:
        worker = db.query(User).filter_by(id=user_id, role="field_worker").first()
        if not worker:
            return jsonify({"error": "Worker not found."}), 404

        worker.is_active = True
        audit = AuditEvent(
            actor_id=g.current_user.id,
            action="WORKER_APPROVED",
            entity_type="user",
            entity_id=str(worker.id),
            ip_address=request.remote_addr,
        )
        db.add(audit)
        db.commit()
        return jsonify({
            "message": f"Worker '{worker.display_name}' has been approved and activated.",
            "user": worker.to_dict(include_private=True),
        })
    finally:
        db.close()


@auth_bp.route("/workers/<int:user_id>/reject", methods=["POST"])
@require_auth(roles=["admin"])
def reject_worker(user_id: int):
    """Administrator rejects a pending field worker."""
    db = SessionLocal()
    try:
        worker = db.query(User).filter_by(id=user_id, role="field_worker").first()
        if not worker:
            return jsonify({"error": "Worker not found."}), 404

        display_name = worker.display_name
        db.delete(worker)
        audit = AuditEvent(
            actor_id=g.current_user.id,
            action="WORKER_REJECTED",
            entity_type="user",
            entity_id=str(user_id),
            ip_address=request.remote_addr,
        )
        db.add(audit)
        db.commit()
        return jsonify({
            "message": f"Worker registration for '{display_name}' has been rejected and removed.",
        })
    finally:
        db.close()


@auth_bp.route("/create-admin", methods=["POST"])
@require_auth(roles=["admin"])
def create_admin():
    """Allows an existing administrator to create a new administrator account."""
    data = request.get_json() or {}
    display_name = data.get("display_name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not display_name or not email or not password:
        return jsonify({"error": "Display name, email, and password are required."}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    db = SessionLocal()
    try:
        existing = db.query(User).filter_by(email=email).first()
        if existing:
            return jsonify({"error": "An account with this email already exists."}), 409

        new_admin = User(
            display_name=display_name,
            email=email,
            role="admin",
            is_active=True,
        )
        new_admin.set_password(password)
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)

        audit = AuditEvent(
            actor_id=g.current_user.id,
            action="ADMIN_ACCOUNT_CREATED",
            entity_type="user",
            entity_id=str(new_admin.id),
            ip_address=request.remote_addr,
        )
        db.add(audit)
        db.commit()

        return jsonify({
            "message": "New Administrator account provisioned successfully.",
            "user": new_admin.to_dict(include_private=True),
        }), 201
    finally:
        db.close()
