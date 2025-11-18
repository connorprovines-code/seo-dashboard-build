"""
AI Assistant models
"""
from sqlalchemy import Column, String, Text, Boolean, TIMESTAMP, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class AiRoleType(enum.Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class PermissionType(enum.Enum):
    read_data = "read_data"
    write_data = "write_data"
    send_emails = "send_emails"
    manage_apis = "manage_apis"


class AiConversation(Base):
    __tablename__ = "ai_conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="ai_conversations")
    project = relationship("Project", back_populates="ai_conversations")
    messages = relationship("AiMessage", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AiConversation(id={self.id}, title={self.title})>"


class AiMessage(Base):
    __tablename__ = "ai_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(Enum(AiRoleType), nullable=False)
    content = Column(Text, nullable=False)
    tool_calls = Column(JSONB, nullable=True)
    tool_results = Column(JSONB, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)

    # Relationships
    conversation = relationship("AiConversation", back_populates="messages")

    __table_args__ = (
        Index('idx_ai_messages_tool_calls', 'tool_calls', postgresql_using='gin'),
        Index('idx_ai_messages_tool_results', 'tool_results', postgresql_using='gin'),
    )

    def __repr__(self):
        return f"<AiMessage(id={self.id}, role={self.role})>"


class AiPermission(Base):
    __tablename__ = "ai_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    permission_type = Column(Enum(PermissionType), nullable=False)
    granted = Column(Boolean, default=False)
    granted_at = Column(TIMESTAMP(timezone=True), nullable=True)
    revoked_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="ai_permissions")

    __table_args__ = (
        Index('idx_ai_permissions_user_permission', 'user_id', 'permission_type', unique=True),
    )

    def __repr__(self):
        return f"<AiPermission(id={self.id}, type={self.permission_type}, granted={self.granted})>"
