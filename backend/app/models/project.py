"""
Project model
"""
from sqlalchemy import Column, String, Boolean, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=False, index=True)
    gsc_connected = Column(Boolean, default=False)
    gsc_refresh_token = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="projects")
    keywords = relationship("Keyword", back_populates="project", cascade="all, delete-orphan")
    rank_tracking = relationship("RankTracking", back_populates="project", cascade="all, delete-orphan")
    competitor_domains = relationship("CompetitorDomain", back_populates="project", cascade="all, delete-orphan")
    backlinks = relationship("Backlink", back_populates="project", cascade="all, delete-orphan")
    outreach_prospects = relationship("OutreachProspect", back_populates="project", cascade="all, delete-orphan")
    ai_conversations = relationship("AiConversation", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, domain={self.domain})>"
