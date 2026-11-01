import os
import sys
import shutil
from pathlib import Path

# Add project root directory to Python path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Configure writable SQLite database location in /tmp when running in Vercel serverless environment
if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    tmp_db = Path("/tmp/civicpulse.db")
    for candidate in [root_dir / "backend" / "civicpulse.db", root_dir / "civicpulse.db"]:
        if candidate.exists() and not tmp_db.exists():
            try:
                shutil.copy2(candidate, tmp_db)
                print(f"Successfully copied {candidate} to /tmp/civicpulse.db")
                break
            except Exception as e:
                print(f"Notice: Failed to copy bundled db to /tmp: {e}")

    if not os.environ.get("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "sqlite:////tmp/civicpulse.db"

from backend.app import create_app
from backend.models import init_db, SessionLocal
from backend.config import Config

flask_app = create_app()

# Auto-seed if database is new or empty in serverless container
try:
    from backend.models.issue import Issue
    db = SessionLocal()
    if db.query(Issue).count() == 0:
        from backend.seeds.seed_data import seed_database
        print("Auto-seeding empty database in serverless container...")
        seed_database(reset=False)
    db.close()
except Exception as e:
    print(f"Container initialization check: {e}")


# WSGI middleware to normalize URL path prefix between Vercel rewrite rules
class PrefixMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        # Strip internal function file prefixes if present
        if path.startswith("/api/index.py"):
            path = path[len("/api/index.py"):]
        elif path.startswith("/index.py"):
            path = path[len("/index.py"):]

        # Normalize paths to match Flask blueprints prefixed with /api
        if not path.startswith("/api") and (path.startswith("/v1") or path == "/health"):
            environ["PATH_INFO"] = "/api" + path
        elif path.startswith("/api"):
            environ["PATH_INFO"] = path
        elif path in ("", "/"):
            environ["PATH_INFO"] = "/api/v1/health"

        return self.wsgi_app(environ, start_response)


app = PrefixMiddleware(flask_app)
handler = app
