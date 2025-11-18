"""API Credential model"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class ApiCredential(Base):
    __tablename__ = "api_credentials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(50), nullable=False)  # 'dataforseo', 'google', 'anthropic'
    credentials_encrypted = Column(String, nullable=False)  # Encrypted JSON blob
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_verified_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="api_credentials")

    # Indexes
    __table_args__ = (
        Index("idx_user_provider", "user_id", "provider", unique=True),
    )
