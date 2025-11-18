"""API Credential schemas"""
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


class ApiCredentialBase(BaseModel):
    provider: str  # 'dataforseo', 'google', 'anthropic'


class ApiCredentialCreate(BaseModel):
    provider: str
    credentials: dict  # Will be encrypted before storage


class ApiCredentialResponse(ApiCredentialBase):
    id: UUID
    user_id: UUID
    is_active: bool
    created_at: datetime
    last_verified_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ApiCredentialCheck(BaseModel):
    exists: bool
    provider: str
    last_verified: Optional[datetime] = None
