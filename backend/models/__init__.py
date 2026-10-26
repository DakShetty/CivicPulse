from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from backend.models.user import Base, User
from backend.models.issue import (
    IssueCategory,
    Issue,
    IssueAttachment,
    StatusHistory,
    NotificationEvent,
    ReportRecord,
    generate_public_reference,
)
from backend.models.cluster import IssueCluster, IssueClusterMember
from backend.models.assignment import Assignment
from backend.models.audit import AuditEvent
from backend.models.processing_job import ProcessingJob

engine = None
_session_factory = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False)
SessionLocal = scoped_session(_session_factory)


def init_db(database_uri: str):
    """Initializes database engine, tables, and session maker."""
    global engine
    connect_args = {}
    if database_uri.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    engine = create_engine(database_uri, connect_args=connect_args, pool_pre_ping=True)
    SessionLocal.configure(bind=engine)
    
    # Create tables if not present
    Base.metadata.create_all(bind=engine)
    return engine, SessionLocal


def get_db():
    """Provides a transactional database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
