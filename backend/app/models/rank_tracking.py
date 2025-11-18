"""
Rank Tracking model
"""
from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey, Enum, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class SearchEngineType(enum.Enum):
    google = "google"
    bing = "bing"
    yahoo = "yahoo"


class RankTracking(Base):
    __tablename__ = "rank_tracking"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    keyword_id = Column(UUID(as_uuid=True), ForeignKey("keywords.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    tracked_url = Column(Text, nullable=False)
    rank_position = Column(Integer, nullable=True)
    search_engine = Column(Enum(SearchEngineType), default=SearchEngineType.google)
    location_code = Column(Integer, nullable=False)
    language_code = Column(String(10), nullable=False, default='en')
    checked_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    keyword = relationship("Keyword", back_populates="rank_tracking")
    project = relationship("Project", back_populates="rank_tracking")

    __table_args__ = (
        Index('idx_rank_tracking_keyword_checked', 'keyword_id', 'checked_at'),
    )

    def __repr__(self):
        return f"<RankTracking(id={self.id}, keyword_id={self.keyword_id}, position={self.rank_position})>"
