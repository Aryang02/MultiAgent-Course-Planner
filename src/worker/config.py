from celery.schedules import crontab

from src.settings import settings

broker_url = settings.CELERY_BROKER_URL
result_backend = settings.CELERY_RESULT_BACKEND

task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]

task_acks_late = True
task_reject_on_worker_lost = True
worker_prefetch_multiplier = 1

task_default_queue = "default"
task_routes = {
    "src.worker.tasks.ingestion.ingest_documents": {"queue": "ingestion"},
    "src.worker.tasks.agents.run_agent_pipeline": {"queue": "agents"},
    "src.worker.tasks.notifications.send_welcome_email": {"queue": "notifications"},
    "src.worker.tasks.maintenance.cleanup_temp_files": {"queue": "maintenance"},
}

task_annotations = {
    "*": {"rate_limit": "100/m"},
    "src.worker.tasks.ingestion.ingest_documents": {
        "autoretry_for": (Exception,),
        "retry_backoff": True,
        "retry_backoff_max": 300,
        "max_retries": 3,
    },
    "src.worker.tasks.agents.run_agent_pipeline": {
        "autoretry_for": (Exception,),
        "retry_backoff": True,
        "retry_backoff_max": 600,
        "max_retries": 3,
    },
}

beat_schedule = {
    "cleanup-temp-files-hourly": {
        "task": "src.worker.tasks.maintenance.cleanup_temp_files",
        "schedule": crontab(minute=0),
    },
}

imports = (
    "src.worker.tasks.ingestion",
    "src.worker.tasks.agents",
    "src.worker.tasks.notifications",
    "src.worker.tasks.maintenance",
)
