"""Rank Tracking router"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta, date
import json

from app.core.database import get_db
from app.core.deps import get_current_user
from app.services.dataforseo import DataForSEOService
from app.routers.api_credentials import get_user_dataforseo_service
from pydantic import BaseModel

router = APIRouter(prefix="/api/projects/{project_id}/rank-tracking", tags=["rank-tracking"])


class RankTrackingCreate(BaseModel):
    keyword_id: UUID
    tracked_url: str
    location_code: int = 2840  # USA
    language_code: str = "en"
    search_engine: SearchEngine = SearchEngine.google


class RankTrackingResponse(BaseModel):
    id: UUID
    keyword_id: UUID
    keyword_text: str
    tracked_url: str
    rank_position: Optional[int]
    search_engine: str
    location_code: int
    language_code: str
    checked_at: datetime

    class Config:
        from_attributes = True


class RankHistoryResponse(BaseModel):
    date: date
    position: Optional[int]

    class Config:
        from_attributes = True


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


@router.post("", response_model=RankTrackingResponse, status_code=status.HTTP_201_CREATED)
async def enable_rank_tracking(
    project_id: UUID,
    tracking_data: RankTrackingCreate,
    project: Project = Depends(get_user_project),
    current_user: User = Depends(get_current_user),
    dataforseo: DataForSEOService = Depends(get_user_dataforseo_service),
    db: Session = Depends(get_db)
):
    """
    Enable rank tracking for a keyword.
    Performs initial rank check.
    """
    # Verify keyword belongs to this project
    keyword = db.query(Keyword).filter(
        Keyword.id == tracking_data.keyword_id,
        Keyword.project_id == project_id
    ).first()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found in this project"
        )

    # Check if already tracking
    existing = db.query(RankTracking).filter(
        RankTracking.keyword_id == tracking_data.keyword_id,
        RankTracking.tracked_url == tracking_data.tracked_url
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already tracking this keyword for this URL"
        )

    # Perform initial rank check
    serp_result = await dataforseo.get_serp_results(
        keyword=keyword.keyword_text,
        location_code=tracking_data.location_code,
        language_code=tracking_data.language_code
    )

    if not serp_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch SERP data: {serp_result.get('error')}"
        )

    # Find rank position for tracked URL
    rank_position = None
    for result in serp_result["results"]:
        if tracking_data.tracked_url in result["url"]:
            rank_position = result["position"]
            break

    # Store rank tracking record
    rank_record = RankTracking(
        keyword_id=tracking_data.keyword_id,
        project_id=project_id,
        tracked_url=tracking_data.tracked_url,
        rank_position=rank_position,
        search_engine=tracking_data.search_engine,
        location_code=tracking_data.location_code,
        language_code=tracking_data.language_code,
        checked_at=datetime.utcnow()
    )
    db.add(rank_record)

    # Store SERP snapshot
    snapshot_date = date.today()
    for result in serp_result["results"]:
        serp_snapshot = SerpSnapshot(
            keyword_id=tracking_data.keyword_id,
            rank_position=result["position"],
            url=result["url"],
            domain=result["domain"],
            title=result.get("title"),
            description=result.get("description"),
            snapshot_date=snapshot_date
        )
        db.add(serp_snapshot)

    # Log API usage
    cost = DataForSEOService.estimate_rank_check_cost(1, live=True)
    api_log = ApiUsageLog(
        user_id=current_user.id,
        api_provider="dataforseo",
        endpoint="serp/organic/live",
        cost=cost,
        response_status=200
    )
    db.add(api_log)

    db.commit()
    db.refresh(rank_record)

    return RankTrackingResponse(
        id=rank_record.id,
        keyword_id=rank_record.keyword_id,
        keyword_text=keyword.keyword_text,
        tracked_url=rank_record.tracked_url,
        rank_position=rank_record.rank_position,
        search_engine=rank_record.search_engine.value,
        location_code=rank_record.location_code,
        language_code=rank_record.language_code,
        checked_at=rank_record.checked_at
    )


@router.get("", response_model=List[RankTrackingResponse])
async def list_tracked_keywords(
    project_id: UUID,
    project: Project = Depends(get_user_project),
    db: Session = Depends(get_db)
):
    """
    List all keywords being tracked for this project.
    Returns the latest rank check for each keyword.
    """
    # Get latest rank for each keyword
    subquery = db.query(
        RankTracking.keyword_id,
        func.max(RankTracking.checked_at).label('max_checked_at')
    ).filter(
        RankTracking.project_id == project_id
    ).group_by(RankTracking.keyword_id).subquery()

    results = db.query(RankTracking, Keyword.keyword_text).join(
        subquery,
        (RankTracking.keyword_id == subquery.c.keyword_id) &
        (RankTracking.checked_at == subquery.c.max_checked_at)
    ).join(Keyword).filter(
        RankTracking.project_id == project_id
    ).all()

    return [
        RankTrackingResponse(
            id=rank.id,
            keyword_id=rank.keyword_id,
            keyword_text=keyword_text,
            tracked_url=rank.tracked_url,
            rank_position=rank.rank_position,
            search_engine=rank.search_engine.value,
            location_code=rank.location_code,
            language_code=rank.language_code,
            checked_at=rank.checked_at
        )
        for rank, keyword_text in results
    ]


@router.get("/{keyword_id}/history")
async def get_rank_history(
    project_id: UUID,
    keyword_id: UUID,
    days: int = 30,
    project: Project = Depends(get_user_project),
    db: Session = Depends(get_db)
):
    """
    Get rank history for a keyword over the specified number of days.
    """
    # Verify keyword belongs to project
    keyword = db.query(Keyword).filter(
        Keyword.id == keyword_id,
        Keyword.project_id == project_id
    ).first()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found in this project"
        )

    # Get rank history
    since_date = datetime.utcnow() - timedelta(days=days)
    history = db.query(
        func.date(RankTracking.checked_at).label('date'),
        func.avg(RankTracking.rank_position).label('avg_position')
    ).filter(
        RankTracking.keyword_id == keyword_id,
        RankTracking.project_id == project_id,
        RankTracking.checked_at >= since_date
    ).group_by(
        func.date(RankTracking.checked_at)
    ).order_by(
        func.date(RankTracking.checked_at)
    ).all()

    return {
        "keyword_id": str(keyword_id),
        "keyword_text": keyword.keyword_text,
        "days": days,
        "history": [
            {
                "date": str(h.date),
                "position": int(h.avg_position) if h.avg_position else None
            }
            for h in history
        ]
    }


@router.get("/{keyword_id}/serp")
async def get_latest_serp(
    project_id: UUID,
    keyword_id: UUID,
    project: Project = Depends(get_user_project),
    db: Session = Depends(get_db)
):
    """
    Get latest SERP snapshot for a keyword.
    """
    # Verify keyword belongs to project
    keyword = db.query(Keyword).filter(
        Keyword.id == keyword_id,
        Keyword.project_id == project_id
    ).first()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found in this project"
        )

    # Get latest SERP snapshot
    latest_snapshot_date = db.query(func.max(SerpSnapshot.snapshot_date)).filter(
        SerpSnapshot.keyword_id == keyword_id
    ).scalar()

    if not latest_snapshot_date:
        return {
            "keyword_id": str(keyword_id),
            "keyword_text": keyword.keyword_text,
            "results": []
        }

    serp_results = db.query(SerpSnapshot).filter(
        SerpSnapshot.keyword_id == keyword_id,
        SerpSnapshot.snapshot_date == latest_snapshot_date
    ).order_by(SerpSnapshot.rank_position).all()

    return {
        "keyword_id": str(keyword_id),
        "keyword_text": keyword.keyword_text,
        "snapshot_date": str(latest_snapshot_date),
        "results": [
            {
                "position": s.rank_position,
                "url": s.url,
                "domain": s.domain,
                "title": s.title,
                "description": s.description
            }
            for s in serp_results
        ]
    }


@router.post("/{keyword_id}/check-now")
async def check_rank_now(
    project_id: UUID,
    keyword_id: UUID,
    project: Project = Depends(get_user_project),
    current_user: User = Depends(get_current_user),
    dataforseo: DataForSEOService = Depends(get_user_dataforseo_service),
    db: Session = Depends(get_db)
):
    """
    Manually trigger a rank check for a keyword.
    """
    # Verify keyword belongs to project and is being tracked
    keyword = db.query(Keyword).filter(
        Keyword.id == keyword_id,
        Keyword.project_id == project_id
    ).first()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found in this project"
        )

    # Get existing tracking settings
    existing_tracking = db.query(RankTracking).filter(
        RankTracking.keyword_id == keyword_id,
        RankTracking.project_id == project_id
    ).order_by(desc(RankTracking.checked_at)).first()

    if not existing_tracking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Keyword is not being tracked. Enable tracking first."
        )

    # Fetch SERP data
    serp_result = await dataforseo.get_serp_results(
        keyword=keyword.keyword_text,
        location_code=existing_tracking.location_code,
        language_code=existing_tracking.language_code
    )

    if not serp_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch SERP data: {serp_result.get('error')}"
        )

    # Find rank position
    rank_position = None
    for result in serp_result["results"]:
        if existing_tracking.tracked_url in result["url"]:
            rank_position = result["position"]
            break

    # Store new rank record
    rank_record = RankTracking(
        keyword_id=keyword_id,
        project_id=project_id,
        tracked_url=existing_tracking.tracked_url,
        rank_position=rank_position,
        search_engine=existing_tracking.search_engine,
        location_code=existing_tracking.location_code,
        language_code=existing_tracking.language_code,
        checked_at=datetime.utcnow()
    )
    db.add(rank_record)

    # Store SERP snapshot
    snapshot_date = date.today()
    # Delete old snapshots from today (if any)
    db.query(SerpSnapshot).filter(
        SerpSnapshot.keyword_id == keyword_id,
        SerpSnapshot.snapshot_date == snapshot_date
    ).delete()

    for result in serp_result["results"]:
        serp_snapshot = SerpSnapshot(
            keyword_id=keyword_id,
            rank_position=result["position"],
            url=result["url"],
            domain=result["domain"],
            title=result.get("title"),
            description=result.get("description"),
            snapshot_date=snapshot_date
        )
        db.add(serp_snapshot)

    # Log API usage
    cost = DataForSEOService.estimate_rank_check_cost(1, live=True)
    api_log = ApiUsageLog(
        user_id=current_user.id,
        api_provider="dataforseo",
        endpoint="serp/organic/live",
        cost=cost,
        response_status=200
    )
    db.add(api_log)

    db.commit()

    return {
        "success": True,
        "keyword_text": keyword.keyword_text,
        "rank_position": rank_position,
        "checked_at": rank_record.checked_at.isoformat()
    }


@router.delete("/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
async def stop_tracking(
    project_id: UUID,
    keyword_id: UUID,
    project: Project = Depends(get_user_project),
    db: Session = Depends(get_db)
):
    """
    Stop tracking a keyword (deletes all rank history).
    """
    # Delete all rank tracking records
    deleted_count = db.query(RankTracking).filter(
        RankTracking.keyword_id == keyword_id,
        RankTracking.project_id == project_id
    ).delete()

    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword tracking not found"
        )

    # Delete SERP snapshots
    db.query(SerpSnapshot).filter(
        SerpSnapshot.keyword_id == keyword_id
    ).delete()

    db.commit()

    return None


@router.get("/stats/overview")
async def get_tracking_overview(
    project_id: UUID,
    project: Project = Depends(get_user_project),
    db: Session = Depends(get_db)
):
    """
    Get overview stats for rank tracking in this project.
    """
    # Total tracked keywords
    total_tracked = db.query(RankTracking.keyword_id).filter(
        RankTracking.project_id == project_id
    ).distinct().count()

    # Average position
    avg_position = db.query(func.avg(RankTracking.rank_position)).filter(
        RankTracking.project_id == project_id,
        RankTracking.rank_position.isnot(None)
    ).scalar()

    # Top 10 count
    top_10_count = db.query(RankTracking.keyword_id).filter(
        RankTracking.project_id == project_id,
        RankTracking.rank_position <= 10
    ).distinct().count()

    # Position distribution
    distribution = {
        "top_3": db.query(RankTracking.keyword_id).filter(
            RankTracking.project_id == project_id,
            RankTracking.rank_position <= 3
        ).distinct().count(),
        "top_10": top_10_count,
        "top_20": db.query(RankTracking.keyword_id).filter(
            RankTracking.project_id == project_id,
            RankTracking.rank_position <= 20
        ).distinct().count(),
        "below_20": db.query(RankTracking.keyword_id).filter(
            RankTracking.project_id == project_id,
            RankTracking.rank_position > 20
        ).distinct().count()
    }

    return {
        "total_tracked": total_tracked,
        "average_position": float(avg_position) if avg_position else None,
        "distribution": distribution
    }
