from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from src.api.limiter import limiter

from src.api.exceptions import ConflictError, UnauthorizedError
from src.auth.auth import create_token, get_user
from src.core.models import User
from src.database.db import get_db
from src.repositories import UserRepository
from src.serializers.backend import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
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

    link = new_user.generate_link()
    send_welcome_email.delay(
        body.email,
        (
            "Welcome to MCP! Your account has been successfully created.\n\n"
            f"Please use the following {link} to login."
        ),
        "Welcome to MCP",
    )
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

    access, refresh = create_token(
        {"sub": str(user.id), "username": user.username, "email": user.email}
    )
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_user)) -> UserResponse:
    return UserResponse.model_validate(user)
