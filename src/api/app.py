import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from alembic import command
from alembic.config import Config
from src.api.deps import get_cors_origins
from src.api.limiter import limiter
from src.api.middleware import (
    RequestIdMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    register_exception_handlers,
)
from src.api.routes import auth, chat, documents, generate, health, study_plans, upload
from src.observability.logging import configure_logging, get_logger
from src.observability.metrics import update_celery_queue_depth
from src.observability.sentry import init_sentry
from src.settings import settings

logger = get_logger(__name__)


def run_migrations() -> None:
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


def create_app(*, run_migrations_on_startup: bool = True) -> FastAPI:
    configure_logging(json_logs=settings.LOG_JSON, log_level=settings.LOG_LEVEL)
    init_sentry()

    app = FastAPI(
        title="MCP API",
        version="1.0.0",
        description="Multi-agent course planner API",
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestIdMiddleware)
    register_exception_handlers(app)

    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        excluded_handlers=["/metrics", "/health"],
    )
    instrumentator.instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

    @app.middleware("http")
    async def refresh_queue_metrics(request, call_next):
        if request.url.path == "/metrics":
            update_celery_queue_depth()
        return await call_next(request)

    if run_migrations_on_startup:

        @app.on_event("startup")
        def on_startup() -> None:
            logging.getLogger(__name__).info("Starting MCP API")
            run_migrations()

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(upload.router)
    app.include_router(documents.router)
    app.include_router(chat.router)
    app.include_router(generate.router)
    app.include_router(study_plans.router)

    return app
