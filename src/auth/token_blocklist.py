import logging
from datetime import UTC, datetime

import redis

from src.settings import settings

logger = logging.getLogger(__name__)

_BLOCKLIST_PREFIX = "token_blocklist:"
_redis_client: redis.Redis | None = None


def _get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


def block_token(jti: str, expires_at: datetime) -> None:
    """Add a JWT ID to the Redis blocklist until the token would have expired."""
    now = datetime.now(UTC)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    ttl_seconds = max(int((expires_at - now).total_seconds()), 1)
    key = f"{_BLOCKLIST_PREFIX}{jti}"
    try:
        _get_redis().setex(key, ttl_seconds, "1")
    except redis.RedisError:
        logger.exception("Failed to block token jti=%s", jti)
        raise


def is_token_blocked(jti: str) -> bool:
    try:
        return _get_redis().exists(f"{_BLOCKLIST_PREFIX}{jti}") == 1
    except redis.RedisError:
        logger.exception("Failed to check token blocklist jti=%s", jti)
        return False
