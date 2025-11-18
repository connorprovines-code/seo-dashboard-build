"""Rank Tracking model"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class SearchEngine(str, enum.Enum):
    google = "google"
    bing = "bing"


class RankTracking(Base):
    __tablename__ = "rank_tracking"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    keyword_id = Column(UUID(as_uuid=True), ForeignKey("keywords.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    tracked_url = Column(String(2048), nullable=False)
    rank_position = Column(Integer, nullable=True)
    search_engine = Column(Enum(SearchEngine), default=SearchEngine.google, nullable=False)
    location_code = Column(Integer, nullable=False)  # DataForSEO location code
    language_code = Column(String(10), nullable=False, default="en")
    checked_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    keyword = relationship("Keyword", back_populates="rank_tracking")
    project = relationship("Project", back_populates="rank_tracking")

    # Indexes
    __table_args__ = (
        Index("idx_keyword_checked", "keyword_id", "checked_at"),
    )
