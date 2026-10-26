from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.models.user import Base


class IssueCluster(Base):
    __tablename__ = "issue_clusters"

    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    representative_issue_id = Column(Integer, ForeignKey("issues.id"), nullable=True)
    status = Column(String(30), default="active", nullable=False)  # active, confirmed, dismissed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    members = relationship("Issue", foreign_keys="Issue.cluster_id", back_populates="cluster")
    cluster_links = relationship("IssueClusterMember", back_populates="cluster", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "representative_issue_id": self.representative_issue_id,
            "status": self.status,
            "member_count": len(self.cluster_links),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "links": [link.to_dict() for link in self.cluster_links],
        }


class IssueClusterMember(Base):
    __tablename__ = "issue_cluster_members"

    id = Column(Integer, primary_key=True)
    cluster_id = Column(Integer, ForeignKey("issue_clusters.id"), nullable=False)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False)
    
    similarity_score = Column(Float, nullable=False)
    distance_km = Column(Float, nullable=False)
    text_similarity = Column(Float, nullable=False)
    similarity_explanation = Column(Text, nullable=False)
    
    # Review workflow as specified in Section 4.3:
    # "Let an administrator confirm, separate, or dismiss a duplicate suggestion."
    reviewed_status = Column(String(30), default="pending_review", nullable=False)  # pending_review, confirmed, separated, dismissed
    reviewed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    cluster = relationship("IssueCluster", back_populates="cluster_links")
    issue = relationship("Issue", foreign_keys=[issue_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by_id])

    def to_dict(self):
        return {
            "id": self.id,
            "cluster_id": self.cluster_id,
            "issue_id": self.issue_id,
            "issue_reference": self.issue.public_reference if self.issue else None,
            "issue_title": self.issue.title if self.issue else None,
            "issue_category": self.issue.category.name if self.issue and self.issue.category else None,
            "similarity_score": round(self.similarity_score, 2),
            "distance_km": round(self.distance_km, 3),
            "text_similarity": round(self.text_similarity, 2),
            "similarity_explanation": self.similarity_explanation,
            "reviewed_status": self.reviewed_status,
            "reviewed_by": self.reviewer.display_name if self.reviewer else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
