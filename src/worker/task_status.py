from celery.result import AsyncResult

from src.serializers.backend import TaskStatusResponse
from src.worker.celery_app import celery_app


def _normalize_status(state: str) -> str:
    mapping = {
        "PENDING": "pending",
        "STARTED": "processing",
        "RETRY": "processing",
        "SUCCESS": "completed",
        "FAILURE": "failed",
        "REVOKED": "failed",
    }
    return mapping.get(state, state.lower())


def get_task_status(task_id: str) -> TaskStatusResponse:
    result = AsyncResult(task_id, app=celery_app)
    status = _normalize_status(result.state)

    if result.successful():
        payload = result.result
        return TaskStatusResponse(
            task_id=task_id,
            status=status,
            result=payload if isinstance(payload, dict) else {"data": payload},
        )

    if result.failed():
        return TaskStatusResponse(
            task_id=task_id,
            status=status,
            error=str(result.result) if result.result else "Task failed",
        )

    return TaskStatusResponse(task_id=task_id, status=status)
