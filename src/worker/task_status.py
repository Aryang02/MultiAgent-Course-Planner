from celery.result import AsyncResult

from src.api.exceptions import ForbiddenError, NotFoundError
from src.serializers.backend import TaskStatusResponse
from src.worker.celery_app import celery_app
from src.worker.task_ownership import get_task_owner


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


def _extract_user_id_from_result(payload) -> str | None:
    if isinstance(payload, dict):
        user_id = payload.get("user_id")
        if user_id:
            return str(user_id)
    return None


def get_task_status(task_id: str, user_id: str) -> TaskStatusResponse:
    owner = get_task_owner(task_id)
    if owner and owner != str(user_id):
        raise ForbiddenError("You do not have access to this task")

    result = AsyncResult(task_id, app=celery_app)
    status = _normalize_status(result.state)

    if result.successful():
        payload = result.result
        result_user_id = _extract_user_id_from_result(payload)
        if owner is None and result_user_id and result_user_id != str(user_id):
            raise ForbiddenError("You do not have access to this task")
        if owner is None and result_user_id is None:
            raise NotFoundError("Task not found")

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

    if owner is None:
        raise NotFoundError("Task not found")

    return TaskStatusResponse(task_id=task_id, status=status)
