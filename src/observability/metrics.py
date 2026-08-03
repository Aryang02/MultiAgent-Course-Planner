import logging

import redis
from prometheus_client import Counter, Gauge, Histogram

from src.settings import settings

logger = logging.getLogger(__name__)

CELERY_QUEUE_DEPTH = Gauge(
    "celery_queue_depth",
    "Number of tasks waiting in a Celery queue",
    ["queue"],
)

AGENT_PIPELINE_DURATION = Histogram(
    "agent_pipeline_duration_seconds",
    "Duration of the full agent pipeline execution",
    buckets=(1, 5, 10, 30, 60, 120, 300, 600),
)

LLM_TOKEN_USAGE = Counter(
    "llm_tokens_total",
    "Total LLM tokens consumed",
    ["model", "token_type"],
)

MONITORED_QUEUES = ("ingestion", "agents", "notifications", "maintenance", "default")


def update_celery_queue_depth() -> None:
    try:
        client = redis.from_url(settings.CELERY_BROKER_URL)
        for queue in MONITORED_QUEUES:
            depth = client.llen(queue)
            CELERY_QUEUE_DEPTH.labels(queue=queue).set(depth)
    except Exception:
        logger.exception("Failed to update Celery queue depth metrics")


def record_pipeline_duration(seconds: float) -> None:
    AGENT_PIPELINE_DURATION.observe(seconds)


def record_llm_tokens(model: str, prompt_tokens: int, completion_tokens: int) -> None:
    if prompt_tokens:
        LLM_TOKEN_USAGE.labels(model=model, token_type="prompt").inc(prompt_tokens)
    if completion_tokens:
        LLM_TOKEN_USAGE.labels(model=model, token_type="completion").inc(completion_tokens)
