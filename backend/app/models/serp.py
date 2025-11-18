"""
SERP Snapshot model
"""
from sqlalchemy import Column, String, Integer, Text, Date, TIMESTAMP, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class SerpSnapshot(Base):
    __tablename__ = "serp_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    keyword_id = Column(UUID(as_uuid=True), ForeignKey("keywords.id", ondelete="CASCADE"), nullable=False, index=True)
    rank_position = Column(Integer, nullable=False)
    url = Column(Text, nullable=False)
    domain = Column(String(255), nullable=False, index=True)
    title = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    serp_features = Column(JSONB, nullable=True)
    snapshot_date = Column(Date, nullable=False, server_default=func.current_date(), index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    keyword = relationship("Keyword", back_populates="serp_snapshots")

    __table_args__ = (
        Index('idx_serp_snapshots_keyword_date', 'keyword_id', 'snapshot_date'),
        Index('idx_serp_snapshots_features', 'serp_features', postgresql_using='gin'),
    )

    def __repr__(self):
        return f"<SerpSnapshot(id={self.id}, domain={self.domain}, position={self.rank_position})>"
