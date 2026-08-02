from fastapi import APIRouter, Depends, Request

from src.api.exceptions import NotFoundError
from src.api.limiter import limiter
from src.auth.auth import get_user
from src.core.models import User
from src.serializers.backend import GenerateRequest, GenerateResponse, TaskStatusResponse
from src.worker.task_status import get_task_status
from src.worker.tasks.agents import run_agent_pipeline

router = APIRouter(prefix="/v1", tags=["generate"])


@router.post("/generate", response_model=GenerateResponse, status_code=202)
@limiter.limit("20/minute")
def generate(
    request: Request,
    body: GenerateRequest,
    user: User = Depends(get_user),
) -> GenerateResponse:
    task = run_agent_pipeline.delay(
        user_id=str(user.id),
        chat_id=str(body.chat_id),
        query=body.query,
    )
    return GenerateResponse(
        task_id=task.id,
        status="pending",
        message="Generation task accepted",
    )


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
def poll_task_status(task_id: str, user: User = Depends(get_user)) -> TaskStatusResponse:
    status = get_task_status(task_id)
    if status.status == "pending" and status.result is None and status.error is None:
        return status
    if status.status == "failed" and status.error and "not found" in status.error.lower():
        raise NotFoundError("Task not found")
    return status
