"""
User model
"""
from sqlalchemy import Column, String, DECIMAL, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    api_credits_remaining = Column(DECIMAL(10, 2), default=0.00)

    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    api_usage_logs = relationship("ApiUsageLog", back_populates="user", cascade="all, delete-orphan")
    api_credentials = relationship("ApiCredential", back_populates="user", cascade="all, delete-orphan")
    ai_conversations = relationship("AiConversation", back_populates="user", cascade="all, delete-orphan")
    ai_permissions = relationship("AiPermission", back_populates="user", cascade="all, delete-orphan")
    email_connection = relationship("EmailConnection", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
