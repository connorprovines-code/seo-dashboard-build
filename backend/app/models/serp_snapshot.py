"""SERP Snapshot model"""
from sqlalchemy import Column, String, Integer, Date, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import date
import uuid

from app.core.database import Base


class SerpSnapshot(Base):
    __tablename__ = "serp_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    keyword_id = Column(UUID(as_uuid=True), ForeignKey("keywords.id", ondelete="CASCADE"), nullable=False)
    rank_position = Column(Integer, nullable=False)
    url = Column(Text, nullable=False)
    domain = Column(String(255), nullable=False)
    title = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    serp_features = Column(JSONB, nullable=True)  # featured_snippet, people_also_ask, etc.
    snapshot_date = Column(Date, default=date.today, nullable=False)

    # Relationships
    keyword = relationship("Keyword", back_populates="serp_snapshots")

    # Indexes
    __table_args__ = (
        Index("idx_keyword_snapshot", "keyword_id", "snapshot_date"),
    )
