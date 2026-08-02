import logging
import uuid

from src.services.agent_pipeline import run_pipeline
from src.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="src.worker.tasks.agents.run_agent_pipeline", bind=True)
def run_agent_pipeline(
    self,
    user_id: str,
    chat_id: str,
    query: str,
    run_id: str | None = None,
) -> dict:
    logger.info(
        "Starting agent pipeline task_id=%s user_id=%s chat_id=%s",
        self.request.id,
        user_id,
        chat_id,
    )
    run_uuid = uuid.UUID(run_id) if run_id else uuid.uuid4()
    result = run_pipeline(
        user_id=uuid.UUID(user_id),
        chat_id=uuid.UUID(chat_id),
        query=query,
        run_id=run_uuid,
    )
    return result
