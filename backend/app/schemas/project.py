"""Project schemas"""
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    domain: str = Field(..., min_length=1, max_length=255)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    domain: Optional[str] = Field(None, min_length=1, max_length=255)
    gsc_connected: Optional[bool] = None


class ProjectResponse(ProjectBase):
    id: UUID
    user_id: UUID
    gsc_connected: bool
    created_at: datetime

    class Config:
        from_attributes = True
