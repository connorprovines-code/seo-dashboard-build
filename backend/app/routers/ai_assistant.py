"""AI Assistant router using Claude"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import BaseModel
from typing import List, Dict, Optional
import json

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import decrypt_data
from app.models.user import User
from app.models.project import Project
from app.models.keyword import Keyword
from app.models.serp_snapshot import SerpSnapshot
from app.models.api_credential import ApiCredential
from app.models.rank_tracking import RankTracking
from app.services.claude_ai import ClaudeAIService
from sqlalchemy import func

router = APIRouter(prefix="/api/ai", tags=["ai-assistant"])


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    project_id: Optional[UUID] = None
    conversation_history: List[ChatMessage] = []


class AnalyzeKeywordsRequest(BaseModel):
    project_id: UUID


class AnalyzeSERPRequest(BaseModel):
    keyword_id: UUID
    project_id: UUID


def get_user_claude_service(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ClaudeAIService:
    """Get Claude service for current user"""
    cred = db.query(ApiCredential).filter(
        ApiCredential.user_id == current_user.id,
        ApiCredential.provider == "anthropic",
        ApiCredential.is_active == True
    ).first()

    if not cred:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anthropic API key not configured. Please add your API key in settings."
        )

    try:
        credentials = json.loads(decrypt_data(cred.credentials_encrypted))
        return ClaudeAIService(api_key=credentials["api_key"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load credentials: {str(e)}"
        )


@router.post("/chat")
async def chat_with_assistant(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    claude: ClaudeAIService = Depends(get_user_claude_service),
    db: Session = Depends(get_db)
):
    """
    Chat with AI assistant.
    Provides SEO advice based on project context.
    """
    project_context = None

    if request.project_id:
        # Get project context
        project = db.query(Project).filter(
            Project.id == request.project_id,
            Project.user_id == current_user.id
        ).first()

        if project:
            # Gather project stats
            keyword_count = db.query(Keyword).filter(
                Keyword.project_id == request.project_id
            ).count()

            avg_position = db.query(func.avg(RankTracking.rank_position)).filter(
                RankTracking.project_id == request.project_id,
                RankTracking.rank_position.isnot(None)
            ).scalar()

            project_context = {
                "name": project.name,
                "domain": project.domain,
                "keyword_count": keyword_count,
                "avg_position": float(avg_position) if avg_position else None
            }

    # Convert Pydantic models to dicts for Claude
    history = [{"role": msg.role, "content": msg.content} for msg in request.conversation_history]

    response = await claude.chat_assistant(
        user_message=request.message,
        conversation_history=history,
        project_context=project_context
    )

    return {
        "success": True,
        "response": response["message"],
        "usage": response.get("usage", {})
    }


@router.post("/analyze/keywords")
async def analyze_keywords(
    request: AnalyzeKeywordsRequest,
    current_user: User = Depends(get_current_user),
    claude: ClaudeAIService = Depends(get_user_claude_service),
    db: Session = Depends(get_db)
):
    """
    AI-powered keyword opportunity analysis.
    Suggests which keywords to prioritize.
    """
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == request.project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Get keywords with data
    keywords = db.query(Keyword).filter(
        Keyword.project_id == request.project_id
    ).all()

    if not keywords:
        return {
            "success": False,
            "message": "No keywords found. Add keywords first."
        }

    # Format for Claude
    keywords_data = [
        {
            "keyword_text": k.keyword_text,
            "search_volume": k.search_volume,
            "keyword_difficulty": k.keyword_difficulty,
            "cpc": float(k.cpc) if k.cpc else None
        }
        for k in keywords
    ]

    response = await claude.analyze_keyword_opportunities(
        keywords=keywords_data,
        project_domain=project.domain
    )

    return response


@router.post("/analyze/serp")
async def analyze_serp(
    request: AnalyzeSERPRequest,
    current_user: User = Depends(get_current_user),
    claude: ClaudeAIService = Depends(get_user_claude_service),
    db: Session = Depends(get_db)
):
    """
    AI-powered SERP analysis.
    Analyzes competition and suggests strategy.
    """
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == request.project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Get keyword
    keyword = db.query(Keyword).filter(
        Keyword.id == request.keyword_id,
        Keyword.project_id == request.project_id
    ).first()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )

    # Get latest SERP snapshot
    latest_date = db.query(
        func.max(SerpSnapshot.snapshot_date)
    ).filter(
        SerpSnapshot.keyword_id == request.keyword_id
    ).scalar()

    if not latest_date:
        return {
            "success": False,
            "message": "No SERP data available. Enable rank tracking first."
        }

    serp_results = db.query(SerpSnapshot).filter(
        SerpSnapshot.keyword_id == request.keyword_id,
        SerpSnapshot.snapshot_date == latest_date
    ).order_by(SerpSnapshot.rank_position).limit(10).all()

    # Format for Claude
    serp_data = [
        {
            "position": s.rank_position,
            "domain": s.domain,
            "title": s.title,
            "url": s.url
        }
        for s in serp_results
    ]

    response = await claude.analyze_serp_competition(
        keyword=keyword.keyword_text,
        serp_results=serp_data,
        our_domain=project.domain
    )

    return response


@router.post("/generate/content-brief")
async def generate_content_brief(
    request: AnalyzeSERPRequest,
    current_user: User = Depends(get_current_user),
    claude: ClaudeAIService = Depends(get_user_claude_service),
    db: Session = Depends(get_db)
):
    """
    Generate AI content brief for a keyword.
    Provides structure, topics, and recommendations.
    """
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == request.project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Get keyword
    keyword = db.query(Keyword).filter(
        Keyword.id == request.keyword_id,
        Keyword.project_id == request.project_id
    ).first()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )

    # Get competitor titles from SERP
    latest_date = db.query(
        func.max(SerpSnapshot.snapshot_date)
    ).filter(
        SerpSnapshot.keyword_id == request.keyword_id
    ).scalar()

    competitor_titles = []
    if latest_date:
        serp_results = db.query(SerpSnapshot.title).filter(
            SerpSnapshot.keyword_id == request.keyword_id,
            SerpSnapshot.snapshot_date == latest_date,
            SerpSnapshot.title.isnot(None)
        ).limit(5).all()

        competitor_titles = [s[0] for s in serp_results]

    response = await claude.generate_content_brief(
        keyword=keyword.keyword_text,
        search_volume=keyword.search_volume or 0,
        competitor_titles=competitor_titles
    )

    return response
