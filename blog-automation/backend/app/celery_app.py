from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "blog_automation",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.content_tasks", "app.tasks.publishing_tasks", "app.tasks.analytics_tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    # 매일 오전 9시 스케줄된 콘텐츠 발행
    "publish-scheduled-content": {
        "task": "app.tasks.publishing_tasks.publish_scheduled_content",
        "schedule": crontab(hour=9, minute=0),
    },
    # 매 시간 성과 데이터 수집
    "collect-analytics": {
        "task": "app.tasks.analytics_tasks.collect_all_analytics",
        "schedule": crontab(minute=0),
    },
    # 매일 자정 일일 리포트 생성
    "generate-daily-report": {
        "task": "app.tasks.analytics_tasks.generate_daily_report",
        "schedule": crontab(hour=0, minute=0),
    },
}