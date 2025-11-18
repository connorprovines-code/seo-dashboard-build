"""Celery application configuration"""
from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "seo_dashboard",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.rank_tracking",
        "app.tasks.keyword_research",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

# Celery Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "daily-rank-checks": {
        "task": "app.tasks.rank_tracking.daily_rank_check_job",
        "schedule": 3600.0 * 24,  # Every 24 hours
    },
}
