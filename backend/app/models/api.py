"""
API Usage and Credentials models
"""
from sqlalchemy import Column, String, Integer, DECIMAL, Text, Boolean, TIMESTAMP, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class ApiUsageLog(Base):
    __tablename__ = "api_usage_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    api_provider = Column(String(100), nullable=False, index=True)
    endpoint = Column(String(255), nullable=False)
    cost = Column(DECIMAL(10, 4), nullable=False)
    request_payload = Column(JSONB, nullable=True)
    response_status = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="api_usage_logs")

    __table_args__ = (
        Index('idx_api_usage_logs_user_created', 'user_id', 'created_at'),
        Index('idx_api_usage_logs_payload', 'request_payload', postgresql_using='gin'),
    )

    def __repr__(self):
        return f"<ApiUsageLog(id={self.id}, provider={self.api_provider}, cost={self.cost})>"


class ApiCredential(Base):
    __tablename__ = "api_credentials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(100), nullable=False)
    credentials_encrypted = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_verified_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="api_credentials")

    __table_args__ = (
        Index('idx_api_credentials_user_provider', 'user_id', 'provider', unique=True),
    )

    def __repr__(self):
        return f"<ApiCredential(id={self.id}, provider={self.provider}, active={self.is_active})>"
