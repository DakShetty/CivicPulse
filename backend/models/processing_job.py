from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from backend.models.user import Base


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    JOB_IMAGE_METADATA = "image_metadata"
    JOB_DUPLICATE_SCAN = "duplicate_scan"
    JOB_REPORT_GENERATION = "report_generation"

    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    id = Column(Integer, primary_key=True)
    job_type = Column(String(50), nullable=False)
    payload_json = Column(Text, nullable=False)
    status = Column(String(30), default=STATUS_PENDING, nullable=False, index=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    error_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "job_type": self.job_type,
            "status": self.status,
            "retry_count": self.retry_count,
            "error_summary": self.error_summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
