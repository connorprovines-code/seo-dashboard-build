"""
Backlink model
"""
from sqlalchemy import Column, String, Integer, Text, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Backlink(Base):
    __tablename__ = "backlinks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    source_domain = Column(String(255), nullable=False, index=True)
    source_url = Column(Text, nullable=False)
    target_url = Column(Text, nullable=False)
    anchor_text = Column(Text, nullable=True)
    domain_rank = Column(Integer, nullable=True)
    first_seen = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    last_checked = Column(TIMESTAMP(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="backlinks")

    def __repr__(self):
        return f"<Backlink(id={self.id}, source={self.source_domain}, target={self.target_url})>"
