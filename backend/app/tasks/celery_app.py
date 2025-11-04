from celery import Celery
from celery.schedules import crontab

# Create a Celery instance
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.tasks.document_tasks", "app.tasks.kpi_tasks", "app.tasks.ai_analysis_tasks"],
)

# Optional configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Celery Beat Schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Calculate KPIs every 5 minutes for all active projects
    'calculate-kpis-every-5-minutes': {
        'task': 'app.tasks.kpi_tasks.calculate_kpis_for_all_projects',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    # Check thresholds every 15 minutes for all active projects
    'check-thresholds-every-15-minutes': {
        'task': 'app.tasks.kpi_tasks.check_thresholds_for_all_projects',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    # Clean up old KPI data once per week (Sunday at 2 AM)
    'cleanup-old-kpi-data-weekly': {
        'task': 'app.tasks.kpi_tasks.cleanup_old_kpi_data',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Sunday 2 AM
        'kwargs': {'days_to_keep': 1095}  # 3 years for ISO 9001:2015
    },
    # Analyze pending documents every hour
    'analyze-pending-documents-hourly': {
        'task': 'app.tasks.ai_analysis_tasks.analyze_pending_documents',
        'schedule': crontab(minute=0),  # Every hour
    },
}

if __name__ == "__main__":
    celery_app.start()