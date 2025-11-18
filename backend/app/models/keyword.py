"""
Keyword model
"""
from sqlalchemy import Column, String, Integer, DECIMAL, TIMESTAMP, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    keyword_text = Column(String(500), nullable=False, index=True)
    search_volume = Column(Integer, nullable=True)
    keyword_difficulty = Column(Integer, nullable=True)
    cpc = Column(DECIMAL(10, 2), nullable=True)
    competition = Column(DECIMAL(5, 4), nullable=True)
    last_refreshed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="keywords")
    rank_tracking = relationship("RankTracking", back_populates="keyword", cascade="all, delete-orphan")
    serp_snapshots = relationship("SerpSnapshot", back_populates="keyword", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_keywords_project_keyword', 'project_id', 'keyword_text'),
        Index('idx_keywords_search_volume', 'search_volume', postgresql_using='btree'),
    )

    def __repr__(self):
        return f"<Keyword(id={self.id}, text={self.keyword_text}, volume={self.search_volume})>"
