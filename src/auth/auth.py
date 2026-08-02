import logging
import uuid

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.auth.token_blocklist import is_token_blocked
from src.core.models import User as UserModel
from src.database.db import get_db
from src.settings import settings

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserModel:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")

        jti = payload.get("jti")
        if jti and is_token_blocked(jti):
            raise HTTPException(status_code=401, detail="Token has been revoked")

        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(UserModel).filter(UserModel.id == uuid.UUID(user_id)).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        request.state.user_id = user.id
        return user
    except (JWTError, ValueError):
        logger.debug("Token validation failed")
        raise HTTPException(status_code=401, detail="Invalid or expired token") from None
