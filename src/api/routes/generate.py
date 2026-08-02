from fastapi import APIRouter, Depends, Request

from src.api.limiter import limiter

from src.api.exceptions import NotImplementedFeatureError
from src.auth.auth import get_user
from src.core.models import User
from src.serializers.backend import GenerateRequest, GenerateResponse, TaskStatusResponse

router = APIRouter(prefix="/v1", tags=["generate"])

# Placeholder until Phase 3 Celery integration
_PENDING_TASKS: dict[str, dict] = {}


@router.post("/generate", response_model=GenerateResponse, status_code=202)
@limiter.limit("20/minute")
def generate(
    request: Request,
    body: GenerateRequest,
    user: User = Depends(get_user),
) -> GenerateResponse:
    # Celery task wiring lands in Phase 3
    raise NotImplementedFeatureError(
        "Async generation will be available in Phase 3. "
        f"Received query for chat {body.chat_id}."
    )


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str, user: User = Depends(get_user)) -> TaskStatusResponse:
    task = _PENDING_TASKS.get(task_id)
    if not task:
        raise NotImplementedFeatureError("Task polling will be available in Phase 3")
    return TaskStatusResponse(**task)
