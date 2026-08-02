import logging

import redis

from src.settings import settings

logger = logging.getLogger(__name__)

_OWNER_PREFIX = "task_owner:"
_OWNER_TTL_SECONDS = 7 * 24 * 3600
_redis_client: redis.Redis | None = None


def _get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


def register_task_owner(task_id: str, user_id: str) -> None:
    try:
        _get_redis().setex(f"{_OWNER_PREFIX}{task_id}", _OWNER_TTL_SECONDS, user_id)
    except redis.RedisError:
        logger.exception("Failed to register task owner task_id=%s", task_id)


def get_task_owner(task_id: str) -> str | None:
    try:
        return _get_redis().get(f"{_OWNER_PREFIX}{task_id}")
    except redis.RedisError:
        logger.exception("Failed to get task owner task_id=%s", task_id)
        return None
