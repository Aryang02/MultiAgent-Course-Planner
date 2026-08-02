import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.exceptions import NotFoundError
from src.auth.auth import get_user
from src.core.models import User
from src.database.db import get_db
from src.repositories import StudyPlanRepository
from src.serializers.backend import StudyPlanListResponse, StudyPlanResponse

router = APIRouter(prefix="/v1", tags=["study-plans"])


@router.get("/study-plans", response_model=StudyPlanListResponse)
def list_study_plans(
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
) -> StudyPlanListResponse:
    plans = StudyPlanRepository(db)
    user_plans = plans.list_for_user(user.id)
    return StudyPlanListResponse(
        plans=[StudyPlanResponse.model_validate(plan) for plan in user_plans]
    )


@router.get("/study-plans/{plan_id}", response_model=StudyPlanResponse)
def get_study_plan(
    plan_id: uuid.UUID,
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
) -> StudyPlanResponse:
    plans = StudyPlanRepository(db)
    plan = plans.get_by_id(user.id, plan_id)
    if not plan:
        raise NotFoundError("Study plan not found")
    return StudyPlanResponse.model_validate(plan)
