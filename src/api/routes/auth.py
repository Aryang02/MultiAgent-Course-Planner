import uuid

from fastapi import APIRouter, Depends, Header, Request
from jose import jwt
from sqlalchemy.orm import Session

from src.api.limiter import limiter

from src.api.exceptions import ConflictError, UnauthorizedError
from src.auth.auth import get_user
from src.auth.token_service import issue_tokens, refresh_tokens, revoke_session
from src.core.models import User
from src.database.db import get_db
from src.repositories import UserRepository
from src.serializers.backend import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from src.settings import settings
from src.utils.email_helper import build_welcome_email, email_helper
from src.worker.tasks.notifications import send_welcome_email

router = APIRouter(prefix="/v1", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> UserResponse:
    users = UserRepository(db)
    if users.get_by_email(body.email) or users.get_by_username(body.username):
        raise ConflictError("Username or email already exists")

    new_user = User(username=body.username, email=body.email)
    new_user.set_password(body.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    login_url = f"{settings.APP_URL.rstrip('/')}/v1/login"
    subject, plain_text, html = build_welcome_email(login_url)
    send_welcome_email.delay(body.email, plain_text, subject, html)
    return UserResponse.model_validate(new_user)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(
    request: Request,
    body: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    users = UserRepository(db)
    user = users.get_by_email(body.email)
    if not user or not user.verify_password(body.password):
        raise UnauthorizedError("Invalid email or password")

    access, refresh = issue_tokens(db, user)
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("30/minute")
def refresh(
    request: Request,
    body: RefreshRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    try:
        access, refresh = refresh_tokens(db, body.refresh_token)
    except ValueError as exc:
        raise UnauthorizedError(str(exc)) from exc

    payload = jwt.decode(access, settings.SECRET_KEY, algorithms=["HS256"])
    user = UserRepository(db).get_by_id(uuid.UUID(payload["sub"]))
    if not user:
        raise UnauthorizedError("User not found")

    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        user=UserResponse.model_validate(user),
    )


@router.post("/logout", status_code=204)
def logout(
    body: LogoutRequest,
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
) -> None:
    access_token = None
    if authorization and authorization.lower().startswith("bearer "):
        access_token = authorization.split(" ", 1)[1]
    revoke_session(db, access_token=access_token, refresh_token=body.refresh_token)


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_user)) -> UserResponse:
    return UserResponse.model_validate(user)
