"""Celery tasks for rank tracking"""
from celery import shared_task
from sqlalchemy.orm import Session
from datetime import datetime, date
import asyncio
import json

from app.core.database import SessionLocal
from app.core.security import decrypt_data
from app.models.keyword import Keyword
from app.models.rank_tracking import RankTracking
from app.models.serp_snapshot import SerpSnapshot
from app.models.api_credential import ApiCredential
from app.models.api_usage_log import ApiUsageLog
from app.services.dataforseo import DataForSEOService


@shared_task(name="app.tasks.rank_tracking.check_keyword_rank")
def check_keyword_rank(keyword_id: str, user_id: str):
    """
    Check rank for a single keyword.
    Called by daily_rank_check_job for each tracked keyword.
    """
    db = SessionLocal()
    try:
        # Get keyword and latest tracking info
        keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
        if not keyword:
            return {"success": False, "error": "Keyword not found"}

        latest_tracking = db.query(RankTracking).filter(
            RankTracking.keyword_id == keyword_id
        ).order_by(RankTracking.checked_at.desc()).first()

        if not latest_tracking:
            return {"success": False, "error": "No tracking configuration found"}

        # Get user's DataForSEO credentials
        cred = db.query(ApiCredential).filter(
            ApiCredential.user_id == user_id,
            ApiCredential.provider == "dataforseo",
            ApiCredential.is_active == True
        ).first()

        if not cred:
            return {"success": False, "error": "DataForSEO credentials not configured"}

        # Decrypt credentials
        credentials = json.loads(decrypt_data(cred.credentials_encrypted))
        dataforseo = DataForSEOService(
            login=credentials["login"],
            password=credentials["password"]
        )

        # Fetch SERP data
        serp_result = asyncio.run(dataforseo.get_serp_results(
            keyword=keyword.keyword_text,
            location_code=latest_tracking.location_code,
            language_code=latest_tracking.language_code
        ))

        if not serp_result["success"]:
            return {"success": False, "error": serp_result.get("error")}

        # Find rank position
        rank_position = None
        for result in serp_result["results"]:
            if latest_tracking.tracked_url in result["url"]:
                rank_position = result["position"]
                break

        # Store new rank record
        rank_record = RankTracking(
            keyword_id=keyword_id,
            project_id=latest_tracking.project_id,
            tracked_url=latest_tracking.tracked_url,
            rank_position=rank_position,
            search_engine=latest_tracking.search_engine,
            location_code=latest_tracking.location_code,
            language_code=latest_tracking.language_code,
            checked_at=datetime.utcnow()
        )
        db.add(rank_record)

        # Store SERP snapshot
        snapshot_date = date.today()
        # Delete old snapshots from today
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
        cost = DataForSEOService.estimate_rank_check_cost(1, live=False)
        api_log = ApiUsageLog(
            user_id=user_id,
            api_provider="dataforseo",
            endpoint="serp/organic/live",
            cost=cost,
            response_status=200
        )
        db.add(api_log)

        db.commit()

        return {
            "success": True,
            "keyword_id": keyword_id,
            "keyword_text": keyword.keyword_text,
            "rank_position": rank_position
        }

    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


@shared_task(name="app.tasks.rank_tracking.daily_rank_check_job")
def daily_rank_check_job():
    """
    Daily job that checks ranks for all tracked keywords.
    Runs at 2 AM daily (configured in celery_app.py).
    """
    db = SessionLocal()
    try:
        # Get all unique keyword_id and user_id combinations being tracked
        tracked = db.query(
            RankTracking.keyword_id,
            Keyword.project_id,
            RankTracking.project_id
        ).join(Keyword).distinct().all()

        # Get user_id for each project
        from app.models.project import Project

        results = []
        for keyword_id, _, project_id in tracked:
            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                # Queue individual rank check task
                result = check_keyword_rank.delay(str(keyword_id), str(project.user_id))
                results.append({
                    "keyword_id": str(keyword_id),
                    "task_id": result.id
                })

        return {
            "success": True,
            "total_keywords": len(results),
            "tasks_queued": results
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        db.close()


@shared_task(name="app.tasks.rank_tracking.check_project_ranks")
def check_project_ranks(project_id: str, user_id: str):
    """
    Check all ranks for a specific project.
    Can be triggered manually by user.
    """
    db = SessionLocal()
    try:
        # Get all tracked keywords for this project
        tracked_keywords = db.query(RankTracking.keyword_id).filter(
            RankTracking.project_id == project_id
        ).distinct().all()

        results = []
        for (keyword_id,) in tracked_keywords:
            result = check_keyword_rank.delay(str(keyword_id), user_id)
            results.append({
                "keyword_id": str(keyword_id),
                "task_id": result.id
            })

        return {
            "success": True,
            "project_id": project_id,
            "total_keywords": len(results),
            "tasks_queued": results
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        db.close()
