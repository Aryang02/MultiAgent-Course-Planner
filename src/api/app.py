import logging

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.api.deps import get_cors_origins
from src.api.limiter import limiter
from src.api.middleware import RequestIdMiddleware, register_exception_handlers
from src.api.routes import auth, chat, generate, health, study_plans, upload
from src.settings import settings

logger = logging.getLogger(__name__)


def run_migrations() -> None:
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


def create_app(*, run_migrations_on_startup: bool = True) -> FastAPI:
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
    app.add_middleware(RequestIdMiddleware)
    register_exception_handlers(app)

    if run_migrations_on_startup:

        @app.on_event("startup")
        def on_startup() -> None:
            logging.basicConfig(level=logging.INFO)
            run_migrations()

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(upload.router)
    app.include_router(chat.router)
    app.include_router(generate.router)
    app.include_router(study_plans.router)

    return app
