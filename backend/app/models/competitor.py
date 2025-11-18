"""
Competitor Domain model
"""
from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class CompetitorDomain(Base):
    __tablename__ = "competitor_domains"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    domain = Column(String(255), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="competitor_domains")

    __table_args__ = (
        Index('idx_competitor_domains_unique', 'project_id', 'domain', unique=True),
    )

    def __repr__(self):
        return f"<CompetitorDomain(id={self.id}, domain={self.domain})>"
