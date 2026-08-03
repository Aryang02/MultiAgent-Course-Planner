from celery import Celery

from src.observability.celery_signals import (  # noqa: F401
    on_task_failure,
    on_task_postrun,
    on_task_prerun,
    on_task_retry,
)
from src.observability.logging import configure_logging
from src.settings import settings

configure_logging(json_logs=settings.LOG_JSON, log_level=settings.LOG_LEVEL)

celery_app = Celery("course_planner")
celery_app.config_from_object("src.worker.config")

# Ensure broker is set even if config object import fails partially
celery_app.conf.broker_url = settings.CELERY_BROKER_URL
celery_app.conf.result_backend = settings.CELERY_RESULT_BACKEND

celery_app.autodiscover_tasks(
    [
        "src.worker.tasks.ingestion",
        "src.worker.tasks.agents",
        "src.worker.tasks.notifications",
        "src.worker.tasks.maintenance",
    ]
)
