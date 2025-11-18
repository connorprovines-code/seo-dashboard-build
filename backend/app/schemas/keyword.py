"""Keyword schemas"""
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional
from decimal import Decimal


class KeywordBase(BaseModel):
    keyword_text: str = Field(..., min_length=1, max_length=500)


class KeywordCreate(KeywordBase):
    pass


class KeywordBulkCreate(BaseModel):
    keywords: list[str] = Field(..., min_items=1)


class KeywordResponse(KeywordBase):
    id: UUID
    project_id: UUID
    search_volume: Optional[int] = None
    keyword_difficulty: Optional[int] = None
    cpc: Optional[Decimal] = None
    competition: Optional[Decimal] = None
    last_refreshed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class KeywordUpdate(BaseModel):
    keyword_text: Optional[str] = Field(None, min_length=1, max_length=500)
