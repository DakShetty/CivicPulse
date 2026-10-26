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
        "sub": user.id,
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
    if not payload:
        return None
    db = SessionLocal()
    try:
        return db.query(User).filter_by(id=payload["sub"], is_active=True).first()
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
    """Citizen reporter self-registration."""
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

        new_user = User(
            display_name=display_name,
            email=email,
            role="reporter",
            is_active=True,
        )
        new_user.set_password(password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

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
