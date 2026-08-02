from celery import Celery

from src.settings import settings

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
