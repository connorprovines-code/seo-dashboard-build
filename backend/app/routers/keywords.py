"""Keywords router"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.keyword import Keyword
from app.models.api_usage_log import ApiUsageLog
from app.schemas.keyword import (
    KeywordCreate,
    KeywordBulkCreate,
    KeywordResponse,
    KeywordUpdate
)
from app.services.dataforseo import DataForSEOService
from app.routers.api_credentials import get_user_dataforseo_service

router = APIRouter(prefix="/api/projects/{project_id}/keywords", tags=["keywords"])


def get_user_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Project:
    """Get project and verify ownership"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return project


@router.post("", response_model=KeywordResponse, status_code=status.HTTP_201_CREATED)
async def add_keyword(
    project_id: UUID,
    keyword_data: KeywordCreate,
    project: Project = Depends(get_user_project),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a single keyword to the project.
    Keyword can be added without data initially.
    """
    # Check if keyword already exists in this project
    existing = db.query(Keyword).filter(
        Keyword.project_id == project_id,
        Keyword.keyword_text == keyword_data.keyword_text
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Keyword already exists in this project"
        )

    # Create keyword
    new_keyword = Keyword(
        project_id=project_id,
        keyword_text=keyword_data.keyword_text
    )

    db.add(new_keyword)
    db.commit()
    db.refresh(new_keyword)

    return new_keyword


@router.post("/bulk", status_code=status.HTTP_201_CREATED)
async def bulk_add_keywords(
    project_id: UUID,
    keywords_data: KeywordBulkCreate,
    project: Project = Depends(get_user_project),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bulk add keywords to the project.
    Duplicates are skipped.
    """
    # Get existing keywords
    existing_keywords = db.query(Keyword.keyword_text).filter(
        Keyword.project_id == project_id
    ).all()
    existing_set = {k[0] for k in existing_keywords}

    # Filter out duplicates
    new_keywords = [k for k in keywords_data.keywords if k not in existing_set]

    if not new_keywords:
        return {
            "success": True,
            "added": 0,
            "skipped": len(keywords_data.keywords),
            "message": "All keywords already exist"
        }

    # Create keyword objects
    keyword_objects = [
        Keyword(project_id=project_id, keyword_text=keyword_text)
        for keyword_text in new_keywords
    ]

    db.bulk_save_objects(keyword_objects)
    db.commit()

    return {
        "success": True,
        "added": len(new_keywords),
        "skipped": len(keywords_data.keywords) - len(new_keywords),
        "message": f"Added {len(new_keywords)} keywords"
    }


@router.get("", response_model=List[KeywordResponse])
async def list_keywords(
    project_id: UUID,
    project: Project = Depends(get_user_project),
    db: Session = Depends(get_db)
):
    """List all keywords for a project"""
    keywords = db.query(Keyword).filter(
        Keyword.project_id == project_id
    ).order_by(Keyword.created_at.desc()).all()

    return keywords


@router.get("/{keyword_id}", response_model=KeywordResponse)
async def get_keyword(
    project_id: UUID,
    keyword_id: UUID,
    project: Project = Depends(get_user_project),
    db: Session = Depends(get_db)
):
    """Get a specific keyword"""
    keyword = db.query(Keyword).filter(
        Keyword.id == keyword_id,
        Keyword.project_id == project_id
    ).first()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )

    return keyword


@router.put("/{keyword_id}/refresh", response_model=KeywordResponse)
async def refresh_keyword_data(
    project_id: UUID,
    keyword_id: UUID,
    project: Project = Depends(get_user_project),
    current_user: User = Depends(get_current_user),
    dataforseo: DataForSEOService = Depends(get_user_dataforseo_service),
    db: Session = Depends(get_db)
):
    """
    Refresh keyword data from DataForSEO API.
    Requires DataForSEO credentials to be configured.
    """
    keyword = db.query(Keyword).filter(
        Keyword.id == keyword_id,
        Keyword.project_id == project_id
    ).first()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )

    # Fetch data from DataForSEO
    result = await dataforseo.get_keyword_data([keyword.keyword_text])

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DataForSEO API error: {result.get('error')}"
        )

    # Update keyword with data
    if result["keywords"]:
        kw_data = result["keywords"][0]
        keyword.search_volume = kw_data.get("search_volume")
        keyword.keyword_difficulty = kw_data.get("keyword_difficulty")
        keyword.cpc = kw_data.get("cpc")
        keyword.competition = kw_data.get("competition")
        keyword.last_refreshed_at = datetime.utcnow()

    # Log API usage
    cost = DataForSEOService.estimate_keyword_research_cost(1)
    api_log = ApiUsageLog(
        user_id=current_user.id,
        api_provider="dataforseo",
        endpoint="bulk_keyword_difficulty",
        cost=cost,
        response_status=200
    )
    db.add(api_log)

    db.commit()
    db.refresh(keyword)

    return keyword


@router.post("/refresh-all")
async def refresh_all_keywords(
    project_id: UUID,
    project: Project = Depends(get_user_project),
    current_user: User = Depends(get_current_user),
    dataforseo: DataForSEOService = Depends(get_user_dataforseo_service),
    db: Session = Depends(get_db)
):
    """
    Refresh all keywords in the project from DataForSEO.
    Batches up to 1000 keywords per request.
    """
    keywords = db.query(Keyword).filter(
        Keyword.project_id == project_id
    ).all()

    if not keywords:
        return {"success": True, "updated": 0, "message": "No keywords to refresh"}

    # Get keyword texts
    keyword_texts = [k.keyword_text for k in keywords]

    # Fetch data from DataForSEO (max 1000 per request)
    result = await dataforseo.get_keyword_data(keyword_texts[:1000])

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DataForSEO API error: {result.get('error')}"
        )

    # Update keywords with data
    keyword_map = {k.keyword_text: k for k in keywords}
    updated_count = 0

    for kw_data in result["keywords"]:
        keyword_text = kw_data.get("keyword")
        if keyword_text in keyword_map:
            keyword = keyword_map[keyword_text]
            keyword.search_volume = kw_data.get("search_volume")
            keyword.keyword_difficulty = kw_data.get("keyword_difficulty")
            keyword.cpc = kw_data.get("cpc")
            keyword.competition = kw_data.get("competition")
            keyword.last_refreshed_at = datetime.utcnow()
            updated_count += 1

    # Log API usage
    cost = DataForSEOService.estimate_keyword_research_cost(len(keyword_texts[:1000]))
    api_log = ApiUsageLog(
        user_id=current_user.id,
        api_provider="dataforseo",
        endpoint="bulk_keyword_difficulty",
        cost=cost,
        response_status=200
    )
    db.add(api_log)

    db.commit()

    return {
        "success": True,
        "updated": updated_count,
        "cost": float(cost),
        "message": f"Refreshed {updated_count} keywords"
    }


@router.get("/cost-estimate/refresh")
async def estimate_refresh_cost(
    project_id: UUID,
    project: Project = Depends(get_user_project),
    db: Session = Depends(get_db)
):
    """Estimate cost to refresh all keywords"""
    keyword_count = db.query(Keyword).filter(
        Keyword.project_id == project_id
    ).count()

    cost = DataForSEOService.estimate_keyword_research_cost(keyword_count)

    return {
        "keyword_count": keyword_count,
        "estimated_cost": float(cost),
        "currency": "USD"
    }


@router.delete("/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_keyword(
    project_id: UUID,
    keyword_id: UUID,
    project: Project = Depends(get_user_project),
    db: Session = Depends(get_db)
):
    """Delete a keyword"""
    keyword = db.query(Keyword).filter(
        Keyword.id == keyword_id,
        Keyword.project_id == project_id
    ).first()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )

    db.delete(keyword)
    db.commit()

    return None
