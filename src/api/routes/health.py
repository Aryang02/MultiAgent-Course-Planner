from fastapi import APIRouter
from sqlalchemy import text

from src.database.db import engine
from src.serializers.backend import HealthResponse, ReadyResponse
from src.settings import settings

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


def _check_database() -> str:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        return "error"


def _check_redis() -> str:
    try:
        import redis

        client = redis.from_url(settings.REDIS_URL)
        client.ping()
        return "ok"
    except Exception:
        return "error"


def _check_pinecone() -> str:
    if not settings.PINECONE_API_KEY:
        return "not_configured"
    try:
        from pinecone import Pinecone

        Pinecone(api_key=settings.PINECONE_API_KEY).list_indexes()
        return "ok"
    except Exception:
        return "error"


@router.get("/ready", response_model=ReadyResponse)
def ready() -> ReadyResponse:
    db_status = _check_database()
    redis_status = _check_redis()
    pinecone_status = _check_pinecone()

    checks = [db_status, redis_status]
    if pinecone_status == "error":
        checks.append(pinecone_status)

    overall = "ok" if all(status == "ok" for status in checks) else "degraded"
    return ReadyResponse(
        status=overall,
        database=db_status,
        redis=redis_status,
        pinecone=pinecone_status,
    )
