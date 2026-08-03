from fastapi.security import OAuth2PasswordBearer
from jose import jwt ,JWTError
import uuid
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from src.settings import settings
from datetime import datetime, timedelta
from core.models import AuthToken, User as UserModel
from database.db import get_db
from sqlalchemy.orm import Session
import traceback

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_token(data: dict, expires_delta: timedelta = None):
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire, "uuid": str(uuid.uuid4())})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
        expire_refresh = datetime.utcnow() + timedelta(days=1)
        refresh_token = jwt.encode({"uuid":str(uuid.uuid4()), "type": "refresh", "exp": expire_refresh}, settings.SECRET_KEY, algorithm="HS256")
        return (encoded_jwt, refresh_token)
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"Failed to create token: {str(e)}")
    
def get_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserModel:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        return user
    except JWTError:
        traceback.print_exc()
        raise HTTPException(status_code=401, detail="Invalid or expired token")