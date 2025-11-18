"""Backlinks router"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import BaseModel
from typing import List
import json

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import decrypt_data
from app.models.user import User
from app.models.project import Project
from app.models.api_credential import ApiCredential
from app.services.backlinks import BacklinkService

router = APIRouter(prefix="/api/projects/{project_id}/backlinks", tags=["backlinks"])


class BacklinkSummaryResponse(BaseModel):
    total_backlinks: int
    referring_domains: int
    referring_ips: int
    domain_rank: int


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


def get_backlink_service(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> BacklinkService:
    """Get backlink service for current user"""
    cred = db.query(ApiCredential).filter(
        ApiCredential.user_id == current_user.id,
        ApiCredential.provider == "dataforseo",
        ApiCredential.is_active == True
    ).first()

    if not cred:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DataForSEO credentials not configured"
        )

    try:
        credentials = json.loads(decrypt_data(cred.credentials_encrypted))
        return BacklinkService(
            login=credentials["login"],
            password=credentials["password"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load credentials: {str(e)}"
        )


@router.get("/summary")
async def get_backlink_summary(
    project_id: UUID,
    project: Project = Depends(get_user_project),
    backlink_service: BacklinkService = Depends(get_backlink_service)
):
    """Get backlink summary for project domain"""
    result = await backlink_service.get_backlink_summary(project.domain)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to fetch backlink data")
        )

    return result["summary"]


@router.get("/list")
async def get_backlinks(
    project_id: UUID,
    limit: int = 100,
    offset: int = 0,
    project: Project = Depends(get_user_project),
    backlink_service: BacklinkService = Depends(get_backlink_service)
):
    """Get detailed backlink list"""
    result = await backlink_service.get_backlinks(
        target_domain=project.domain,
        limit=limit,
        offset=offset
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to fetch backlinks")
        )

    return {
        "backlinks": result["backlinks"],
        "count": result["count"],
        "limit": limit,
        "offset": offset
    }


@router.get("/referring-domains")
async def get_referring_domains(
    project_id: UUID,
    limit: int = 100,
    project: Project = Depends(get_user_project),
    backlink_service: BacklinkService = Depends(get_backlink_service)
):
    """Get referring domains"""
    result = await backlink_service.get_referring_domains(
        target_domain=project.domain,
        limit=limit
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to fetch referring domains")
        )

    return {
        "domains": result["domains"],
        "count": result["count"]
    }
