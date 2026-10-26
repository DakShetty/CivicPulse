import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.models.user import Base


def generate_public_reference():
    """Generates a clean reference like CP-2026-AB12."""
    year = datetime.now(timezone.utc).year
    suffix = uuid.uuid4().hex[:6].upper()
    return f"CP-{year}-{suffix}"


class IssueCategory(Base):
    __tablename__ = "issue_categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    code = Column(String(40), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    default_severity_weight = Column(Float, default=1.0)
    sla_hours = Column(Integer, default=72)
    is_active = Column(Boolean, default=True, nullable=False)

    issues = relationship("Issue", back_populates="category")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "default_severity_weight": self.default_severity_weight,
            "sla_hours": self.sla_hours,
            "is_active": self.is_active,
        }


class Issue(Base):
    __tablename__ = "issues"

    # Status constants as requested in spec
    STATUS_SUBMITTED = "Submitted"
    STATUS_TRIAGED = "Triaged"
    STATUS_ASSIGNED = "Assigned"
    STATUS_IN_PROGRESS = "In Progress"
    STATUS_RESOLVED = "Resolved"
    STATUS_VERIFIED = "Verified"
    STATUS_REJECTED = "Rejected"

    ALL_STATUSES = [
        STATUS_SUBMITTED,
        STATUS_TRIAGED,
        STATUS_ASSIGNED,
        STATUS_IN_PROGRESS,
        STATUS_RESOLVED,
        STATUS_VERIFIED,
        STATUS_REJECTED,
    ]

    id = Column(Integer, primary_key=True)
    public_reference = Column(String(32), unique=True, nullable=False, index=True, default=generate_public_reference)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("issue_categories.id"), nullable=False)
    
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    
    # Approximate location
    approximate_address = Column(String(255), nullable=True)
    ward_or_district = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Severity & Priority
    severity = Column(Integer, default=3, nullable=False)  # 1 (low) to 5 (critical)
    safety_hazard = Column(Boolean, default=False)
    impacts_critical_infrastructure = Column(Boolean, default=False)
    priority_score = Column(Float, default=25.0)
    priority_explanation = Column(Text, nullable=True)
    
    # Workflow
    status = Column(String(30), default=STATUS_SUBMITTED, nullable=False, index=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Cluster reference
    cluster_id = Column(Integer, ForeignKey("issue_clusters.id"), nullable=True)
    is_cluster_representative = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    acknowledged_at = Column(DateTime, nullable=True)
    assigned_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    category = relationship("IssueCategory", back_populates="issues")
    reporter = relationship("User", foreign_keys=[reporter_id])
    attachments = relationship("IssueAttachment", back_populates="issue", cascade="all, delete-orphan")
    status_history = relationship("StatusHistory", back_populates="issue", order_by="StatusHistory.created_at.desc()", cascade="all, delete-orphan")
    assignment = relationship("Assignment", back_populates="issue", uselist=False, cascade="all, delete-orphan")
    cluster = relationship("IssueCluster", foreign_keys=[cluster_id], back_populates="members")

    def to_dict(self, include_private: bool = False) -> dict:
        data = {
            "id": self.id,
            "public_reference": self.public_reference,
            "category": self.category.to_dict() if self.category else None,
            "title": self.title,
            "description": self.description,
            "approximate_address": self.approximate_address,
            "ward_or_district": self.ward_or_district,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "severity": self.severity,
            "safety_hazard": self.safety_hazard,
            "impacts_critical_infrastructure": self.impacts_critical_infrastructure,
            "priority_score": round(self.priority_score, 1) if self.priority_score is not None else 0,
            "priority_explanation": self.priority_explanation,
            "status": self.status,
            "cluster_id": self.cluster_id,
            "is_cluster_representative": self.is_cluster_representative,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "attachments_count": len(self.attachments),
        }
        
        if self.assignment and self.assignment.field_worker:
            data["assigned_worker"] = {
                "id": self.assignment.field_worker.id,
                "display_name": self.assignment.field_worker.display_name,
            }
        else:
            data["assigned_worker"] = None

        if include_private:
            data["rejection_reason"] = self.rejection_reason
            if self.reporter:
                data["reporter"] = {
                    "id": self.reporter.id,
                    "display_name": self.reporter.display_name,
                    "email": self.reporter.email,
                }
        return data


class IssueAttachment(Base):
    __tablename__ = "issue_attachments"

    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False)
    s3_object_key = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    storage_driver = Column(String(20), default="local")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    issue = relationship("Issue", back_populates="attachments")

    def to_dict(self):
        return {
            "id": self.id,
            "issue_id": self.issue_id,
            "original_filename": self.original_filename,
            "file_type": self.file_type,
            "file_size_bytes": self.file_size_bytes,
            "s3_object_key": self.s3_object_key,
            "storage_driver": self.storage_driver,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class StatusHistory(Base):
    __tablename__ = "status_history"

    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False)
    old_status = Column(String(30), nullable=True)
    new_status = Column(String(30), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    issue = relationship("Issue", back_populates="status_history")
    actor = relationship("User", foreign_keys=[actor_id])

    def to_dict(self):
        return {
            "id": self.id,
            "issue_id": self.issue_id,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "actor_name": self.actor.display_name if self.actor else "System",
            "actor_role": self.actor.role if self.actor else "system",
            "note": self.note,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class NotificationEvent(Base):
    __tablename__ = "notification_events"

    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=True)
    channel = Column(String(30), nullable=False)  # in_app, email, sns
    recipient = Column(String(120), nullable=True)
    subject = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String(30), default="sent")  # sent, failed, simulated
    error_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "issue_id": self.issue_id,
            "channel": self.channel,
            "recipient": self.recipient,
            "subject": self.subject,
            "status": self.status,
            "error_summary": self.error_summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ReportRecord(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    report_type = Column(String(30), nullable=False)  # summary_csv, summary_pdf
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    filters_json = Column(Text, nullable=True)
    s3_object_key = Column(String(255), nullable=True)
    file_size_bytes = Column(Integer, default=0)
    status = Column(String(30), default="completed")  # pending, completed, failed
    error_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "report_type": self.report_type,
            "s3_object_key": self.s3_object_key,
            "file_size_bytes": self.file_size_bytes,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
