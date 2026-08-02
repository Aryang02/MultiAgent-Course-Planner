from fastapi import APIRouter
from sqlalchemy import text

from src.database.db import engine
from src.serializers.backend import HealthResponse, ReadyResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/ready", response_model=ReadyResponse)
def ready() -> ReadyResponse:
    db_status = "ok"
    redis_status = "ok"

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    try:
        import redis
        from src.settings import settings

        client = redis.from_url(settings.REDIS_URL)
        client.ping()
    except Exception:
        redis_status = "error"

    overall = "ok" if db_status == "ok" and redis_status == "ok" else "degraded"
    return ReadyResponse(status=overall, database=db_status, redis=redis_status)
