"""
Outreach Prospect model
"""
from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class OutreachStatusType(enum.Enum):
    prospect = "prospect"
    contacted = "contacted"
    replied = "replied"
    placed = "placed"
    rejected = "rejected"


class OutreachProspect(Base):
    __tablename__ = "outreach_prospects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    domain = Column(String(255), nullable=False, index=True)
    domain_authority = Column(Integer, nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_name = Column(String(255), nullable=True)
    outreach_status = Column(Enum(OutreachStatusType), default=OutreachStatusType.prospect, index=True)
    last_contacted_at = Column(TIMESTAMP(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="outreach_prospects")

    def __repr__(self):
        return f"<OutreachProspect(id={self.id}, domain={self.domain}, status={self.outreach_status})>"
