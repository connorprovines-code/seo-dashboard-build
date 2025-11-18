"""API Usage Log model"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class ApiUsageLog(Base):
    __tablename__ = "api_usage_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    api_provider = Column(String(50), nullable=False)  # 'dataforseo', 'google'
    endpoint = Column(String(255), nullable=False)
    cost = Column(Numeric(10, 4), nullable=False)
    request_payload = Column(JSONB, nullable=True)
    response_status = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="api_usage_logs")

    # Indexes
    __table_args__ = (
        Index("idx_user_created", "user_id", "created_at"),
    )
