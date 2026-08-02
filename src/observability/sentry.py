import logging

from src.settings import settings

logger = logging.getLogger(__name__)


def init_sentry() -> None:
    if not settings.SENTRY_DSN:
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.celery import CeleryIntegration
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        from sentry_sdk.integrations.redis import RedisIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    except ImportError:
        logger.warning("sentry-sdk is not installed; skipping Sentry initialization")
        return

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        integrations=[
            FastApiIntegration(),
            CeleryIntegration(),
            SqlalchemyIntegration(),
            RedisIntegration(),
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
        ],
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        send_default_pii=False,
    )
    logger.info("Sentry initialized for environment=%s", settings.ENVIRONMENT)


def set_sentry_user(user_id: str | None) -> None:
    if not settings.SENTRY_DSN:
        return
    try:
        import sentry_sdk

        if user_id:
            sentry_sdk.set_user({"id": user_id})
        else:
            sentry_sdk.set_user(None)
    except ImportError:
        return


def set_sentry_tags(**tags: str | None) -> None:
    if not settings.SENTRY_DSN:
        return
    try:
        import sentry_sdk

        for key, value in tags.items():
            if value is not None:
                sentry_sdk.set_tag(key, value)
    except ImportError:
        return
