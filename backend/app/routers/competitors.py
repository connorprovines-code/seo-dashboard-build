"""Competitors router"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List
from uuid import UUID
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.competitor import CompetitorDomain
from app.models.keyword import Keyword
from app.models.serp_snapshot import SerpSnapshot
from app.models.rank_tracking import RankTracking

router = APIRouter(prefix="/api/projects/{project_id}/competitors", tags=["competitors"])


class CompetitorCreate(BaseModel):
    domain: str
    notes: str | None = None


class CompetitorResponse(BaseModel):
    id: UUID
    domain: str
    notes: str | None
    created_at: str

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


@router.post("", response_model=CompetitorResponse, status_code=status.HTTP_201_CREATED)
def add_competitor(
    project_id: UUID,
    competitor_data: CompetitorCreate,
    project: Project = Depends(get_user_project),
    db: Session = Depends(get_db)
):
    """Add a competitor domain to track"""
    # Check if already exists
    existing = db.query(CompetitorDomain).filter(
        CompetitorDomain.project_id == project_id,
        CompetitorDomain.domain == competitor_data.domain
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Competitor already exists"
        )

    competitor = CompetitorDomain(
        project_id=project_id,
        domain=competitor_data.domain,
        notes=competitor_data.notes
    )

    db.add(competitor)
    db.commit()
    db.refresh(competitor)

    return competitor


@router.get("", response_model=List[CompetitorResponse])
def list_competitors(
    project_id: UUID,
    project: Project = Depends(get_user_project),
    db: Session = Depends(get_db)
):
    """List all competitors for this project"""
    competitors = db.query(CompetitorDomain).filter(
        CompetitorDomain.project_id == project_id
    ).all()

    return competitors


@router.get("/analysis/keyword-overlap")
def analyze_keyword_overlap(
    project_id: UUID,
    project: Project = Depends(get_user_project),
    db: Session = Depends(get_db)
):
    """
    Analyze keyword overlap with competitors.
    Shows which keywords you and competitors rank for.
    """
    # Get all keywords for this project
    keywords = db.query(Keyword).filter(Keyword.project_id == project_id).all()

    if not keywords:
        return {"overlap": [], "total_keywords": 0}

    # Get competitors
    competitors = db.query(CompetitorDomain).filter(
        CompetitorDomain.project_id == project_id
    ).all()

    if not competitors:
        return {"overlap": [], "total_keywords": len(keywords), "message": "No competitors added yet"}

    # For each keyword, check which competitors rank for it
    overlap_data = []

    for keyword in keywords:
        # Get latest SERP snapshot
        latest_snapshot = db.query(
            func.max(SerpSnapshot.snapshot_date)
        ).filter(
            SerpSnapshot.keyword_id == keyword.id
        ).scalar()

        if not latest_snapshot:
            continue

        # Get all domains ranking for this keyword
        ranking_domains = db.query(SerpSnapshot.domain).filter(
            SerpSnapshot.keyword_id == keyword.id,
            SerpSnapshot.snapshot_date == latest_snapshot
        ).distinct().all()

        ranking_domains_set = {d[0] for d in ranking_domains}

        # Check which competitors rank
        competitors_ranking = []
        for comp in competitors:
            if comp.domain in ranking_domains_set:
                # Get their position
                position = db.query(SerpSnapshot.rank_position).filter(
                    SerpSnapshot.keyword_id == keyword.id,
                    SerpSnapshot.snapshot_date == latest_snapshot,
                    SerpSnapshot.domain == comp.domain
                ).first()

                competitors_ranking.append({
                    "domain": comp.domain,
                    "position": position[0] if position else None
                })

        # Get our position
        our_rank = db.query(RankTracking.rank_position).filter(
            RankTracking.keyword_id == keyword.id,
            RankTracking.project_id == project_id
        ).order_by(RankTracking.checked_at.desc()).first()

        overlap_data.append({
            "keyword": keyword.keyword_text,
            "our_position": our_rank[0] if our_rank else None,
            "competitors_ranking": competitors_ranking,
            "total_competitors_ranking": len(competitors_ranking)
        })

    return {
        "total_keywords": len(keywords),
        "keywords_analyzed": len(overlap_data),
        "overlap": overlap_data
    }


@router.get("/analysis/gap-analysis")
def gap_analysis(
    project_id: UUID,
    competitor_id: UUID,
    project: Project = Depends(get_user_project),
    db: Session = Depends(get_db)
):
    """
    Gap analysis: Keywords competitor ranks for that you don't.
    Opportunity finder.
    """
    # Verify competitor belongs to project
    competitor = db.query(CompetitorDomain).filter(
        CompetitorDomain.id == competitor_id,
        CompetitorDomain.project_id == project_id
    ).first()

    if not competitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitor not found"
        )

    # Get keywords we're tracking
    our_keywords = db.query(Keyword.keyword_text).filter(
        Keyword.project_id == project_id
    ).all()
    our_keywords_set = {k[0] for k in our_keywords}

    # Get all SERP snapshots where competitor appears
    competitor_serps = db.query(
        SerpSnapshot.keyword_id,
        SerpSnapshot.rank_position,
        Keyword.keyword_text
    ).join(Keyword).filter(
        SerpSnapshot.domain == competitor.domain,
        Keyword.project_id == project_id
    ).distinct(SerpSnapshot.keyword_id).all()

    # Find gaps (keywords they rank for, we don't track or don't rank well)
    gaps = []
    for keyword_id, comp_position, keyword_text in competitor_serps:
        # Check our position
        our_rank = db.query(RankTracking.rank_position).filter(
            RankTracking.keyword_id == keyword_id,
            RankTracking.project_id == project_id
        ).order_by(RankTracking.checked_at.desc()).first()

        our_position = our_rank[0] if our_rank else None

        # It's a gap if:
        # 1. We don't rank at all, OR
        # 2. They rank better than us
        if our_position is None or (comp_position < our_position):
            gaps.append({
                "keyword": keyword_text,
                "competitor_position": comp_position,
                "our_position": our_position,
                "opportunity_score": comp_position,  # Lower is better opportunity
                "gap_size": (our_position - comp_position) if our_position else 100
            })

    # Sort by opportunity (best competitor positions first)
    gaps.sort(key=lambda x: x["opportunity_score"])

    return {
        "competitor": competitor.domain,
        "total_gaps": len(gaps),
        "opportunities": gaps[:50]  # Top 50 opportunities
    }


@router.get("/analysis/serp-features")
def analyze_serp_features(
    project_id: UUID,
    project: Project = Depends(get_user_project),
    db: Session = Depends(get_db)
):
    """
    Analyze SERP features across all keywords.
    Shows featured snippets, PAA, etc. opportunities.
    """
    keywords = db.query(Keyword).filter(Keyword.project_id == project_id).all()

    features_summary = []

    for keyword in keywords:
        # Get latest snapshot
        latest_date = db.query(
            func.max(SerpSnapshot.snapshot_date)
        ).filter(
            SerpSnapshot.keyword_id == keyword.id
        ).scalar()

        if not latest_date:
            continue

        # Get SERP features
        serp_with_features = db.query(SerpSnapshot).filter(
            SerpSnapshot.keyword_id == keyword.id,
            SerpSnapshot.snapshot_date == latest_date,
            SerpSnapshot.serp_features.isnot(None)
        ).first()

        if serp_with_features and serp_with_features.serp_features:
            features_summary.append({
                "keyword": keyword.keyword_text,
                "features": serp_with_features.serp_features,
                "snapshot_date": str(latest_date)
            })

    return {
        "total_keywords": len(keywords),
        "keywords_with_features": len(features_summary),
        "features": features_summary
    }


@router.delete("/{competitor_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_competitor(
    project_id: UUID,
    competitor_id: UUID,
    project: Project = Depends(get_user_project),
    db: Session = Depends(get_db)
):
    """Remove a competitor"""
    competitor = db.query(CompetitorDomain).filter(
        CompetitorDomain.id == competitor_id,
        CompetitorDomain.project_id == project_id
    ).first()

    if not competitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitor not found"
        )

    db.delete(competitor)
    db.commit()

    return None
