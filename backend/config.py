import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

# Load .env if present
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base application configuration with local fallbacks and AWS integration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "civicpulse-local-dev-key-change-in-prod-xyz")
    ENV = os.environ.get("FLASK_ENV", "development")
    DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"

    # Database
    # Local default: SQLite in backend directory (or /tmp if running in serverless like Vercel/Lambda)
    # RDS MySQL: mysql+pymysql://<user>:<password>@<rds-endpoint>:3306/civicpulse
    _is_serverless = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
    _default_db_path = "/tmp/civicpulse.db" if _is_serverless else str(BASE_DIR / 'civicpulse.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{_default_db_path}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Storage: 'local' or 's3'
    STORAGE_DRIVER = os.environ.get("STORAGE_DRIVER", "local")
    LOCAL_STORAGE_DIR = Path("/tmp/storage") if _is_serverless else (BASE_DIR / "storage")
    S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "civicpulse-demo-bucket")
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

    # Queue: 'local' (database table polling) or 'sqs'
    QUEUE_DRIVER = os.environ.get("QUEUE_DRIVER", "local")
    SQS_QUEUE_URL = os.environ.get("SQS_QUEUE_URL", "")
    SQS_DLQ_URL = os.environ.get("SQS_DLQ_URL", "")

    # Notification: 'local' (db events) or 'sns'
    NOTIFICATION_DRIVER = os.environ.get("NOTIFICATION_DRIVER", "local")
    SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")

    # CloudWatch Logs
    LOGGING_DRIVER = os.environ.get("LOGGING_DRIVER", "local")
    CLOUDWATCH_LOG_GROUP = os.environ.get("CLOUDWATCH_LOG_GROUP", "/civicpulse/app")

    # Parameter Store
    USE_PARAMETER_STORE = os.environ.get("USE_PARAMETER_STORE", "false").lower() == "true"
    SSM_PARAM_PREFIX = os.environ.get("SSM_PARAM_PREFIX", "/civicpulse/prod/")

    # CORS
    CORS_ORIGIN = os.environ.get("CORS_ORIGIN", "http://localhost:5173")

    # File Upload limits (max 8MB)
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

    # SLA and Scoring defaults
    SLA_ACKNOWLEDGE_HOURS = int(os.environ.get("SLA_ACKNOWLEDGE_HOURS", 24))
    SLA_RESOLVE_HOURS = int(os.environ.get("SLA_RESOLVE_HOURS", 72))

    # Duplicate clustering defaults
    DUPLICATE_DISTANCE_KM_THRESHOLD = float(os.environ.get("DUPLICATE_DISTANCE_KM_THRESHOLD", 0.35))
    DUPLICATE_TIME_WINDOW_DAYS = int(os.environ.get("DUPLICATE_TIME_WINDOW_DAYS", 45))
    DUPLICATE_SIMILARITY_SCORE_THRESHOLD = float(os.environ.get("DUPLICATE_SIMILARITY_SCORE_THRESHOLD", 0.55))


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    STORAGE_DRIVER = "local"
    QUEUE_DRIVER = "local"
    NOTIFICATION_DRIVER = "local"


class ProductionConfig(Config):
    DEBUG = False
