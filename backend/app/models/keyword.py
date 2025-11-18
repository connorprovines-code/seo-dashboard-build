"""Keyword model"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    keyword_text = Column(String(500), nullable=False)
    search_volume = Column(Integer, nullable=True)
    keyword_difficulty = Column(Integer, nullable=True)
    cpc = Column(Numeric(10, 2), nullable=True)
    competition = Column(Numeric(5, 2), nullable=True)
    last_refreshed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="keywords")
    rank_tracking = relationship("RankTracking", back_populates="keyword", cascade="all, delete-orphan")
    serp_snapshots = relationship("SerpSnapshot", back_populates="keyword", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_project_keyword", "project_id", "keyword_text"),
    )
