import logging
import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.auth.token_blocklist import block_token
from src.core.models import User
from src.repositories.base import AuthTokenRepository
from src.settings import settings

logger = logging.getLogger(__name__)

ACCESS_TOKEN_TTL = timedelta(minutes=15)
REFRESH_TOKEN_TTL = timedelta(days=7)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _encode(payload: dict) -> str:
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def issue_tokens(db: Session, user: User) -> tuple[str, str]:
    access_jti = str(uuid.uuid4())
    refresh_jti = str(uuid.uuid4())
    now = _utcnow()
    access_expires = now + ACCESS_TOKEN_TTL
    refresh_expires = now + REFRESH_TOKEN_TTL

    access_token = _encode(
        {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "jti": access_jti,
            "type": "access",
            "exp": access_expires,
        }
    )
    refresh_token = _encode(
        {
            "sub": str(user.id),
            "jti": refresh_jti,
            "type": "refresh",
            "exp": refresh_expires,
        }
    )

    tokens = AuthTokenRepository(db)
    tokens.create(
        user_id=user.id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=access_expires,
        refresh_expires_at=refresh_expires,
    )
    db.commit()
    return access_token, refresh_token


def refresh_tokens(db: Session, refresh_token: str) -> tuple[str, str]:
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
    except JWTError as exc:
        raise ValueError("Invalid or expired refresh token") from exc

    if payload.get("type") != "refresh":
        raise ValueError("Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("Invalid refresh token")

    token_repo = AuthTokenRepository(db)
    record = token_repo.get_active_by_refresh_token(refresh_token)
    if not record:
        raise ValueError("Refresh token revoked or expired")

    user = token_repo.get_user(uuid.UUID(user_id))
    if not user:
        raise ValueError("User not found")

    token_repo.mark_refresh_expired(record)
    access_token, new_refresh_token = issue_tokens(db, user)
    return access_token, new_refresh_token


def revoke_session(
    db: Session,
    *,
    access_token: str | None = None,
    refresh_token: str | None = None,
) -> None:
    if access_token:
        try:
            payload = jwt.decode(
                access_token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
                options={"verify_exp": False},
            )
            jti = payload.get("jti")
            exp = payload.get("exp")
            if jti and exp:
                expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
                block_token(jti, expires_at)
        except JWTError:
            logger.warning("Could not decode access token during logout")

    if refresh_token:
        token_repo = AuthTokenRepository(db)
        record = token_repo.get_active_by_refresh_token(refresh_token)
        if record:
            token_repo.mark_refresh_expired(record)
            db.commit()
