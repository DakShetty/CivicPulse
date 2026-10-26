import pytest
from backend.app import create_app
from backend.config import TestingConfig
from backend.models import init_db, SessionLocal
from backend.models.user import User
from backend.models.issue import IssueCategory, Issue


@pytest.fixture
def client():
    app = create_app(TestingConfig)
    with app.test_client() as client:
        db = SessionLocal()
        try:
            cat = db.query(IssueCategory).filter_by(code="pothole").first()
            if not cat:
                cat = IssueCategory(name="Pothole Damage", code="pothole", default_severity_weight=1.0)
                db.add(cat)

            admin = db.query(User).filter_by(email="admin@test.local").first()
            if not admin:
                admin = User(display_name="Test Admin", email="admin@test.local", role="admin")
                admin.set_password("Secret123!")
                db.add(admin)

            db.commit()
        finally:
            db.close()
        yield client
        SessionLocal.remove()


def test_health_endpoint(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


def test_auth_login(client):
    res = client.post("/api/v1/auth/login", json={
        "email": "admin@test.local",
        "password": "Secret123!"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "token" in data
    assert data["user"]["role"] == "admin"


def test_public_issue_submission_and_track(client):
    # Submit issue
    submit_res = client.post("/api/v1/issues", json={
        "category_id": 1,
        "title": "Broken asphalt pothole",
        "description": "Hazardous road defect causing slowdowns",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "ward_or_district": "Central Ward",
        "approximate_address": "Market St",
        "severity": 4,
        "safety_hazard": True,
    })
    assert submit_res.status_code == 201
    submit_data = submit_res.get_json()
    assert "public_reference" in submit_data
    ref = submit_data["public_reference"]

    # Public tracking by reference
    track_res = client.get(f"/api/v1/issues/track/{ref}")
    assert track_res.status_code == 200
    track_data = track_res.get_json()
    assert track_data["public_reference"] == ref
    assert track_data["status"] == Issue.STATUS_SUBMITTED
    assert len(track_data["history"]) >= 1
