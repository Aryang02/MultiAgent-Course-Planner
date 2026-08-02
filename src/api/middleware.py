import logging
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.api.exceptions import AppError

logger = logging.getLogger(__name__)


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


def register_exception_handlers(app) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        request_id = getattr(request.state, "request_id", None)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "request_id": request_id},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", None)
        logger.exception("Unhandled error request_id=%s", request_id)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "request_id": request_id},
        )
