"""Celery application. Full implementation in Phase 3."""

try:
    from celery import Celery
    from src.settings import settings

    celery_app = Celery("course_planner")
    celery_app.conf.update(
        broker_url=settings.CELERY_BROKER_URL,
        result_backend=settings.CELERY_RESULT_BACKEND,
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        task_acks_late=True,
        worker_prefetch_multiplier=1,
    )
except ImportError:
    celery_app = None
