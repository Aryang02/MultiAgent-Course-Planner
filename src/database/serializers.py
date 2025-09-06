from pydantic import BaseModel
from typing import List
import uuid
import datetime

class User(BaseModel):
    id: uuid
    name: str
    email: str
    password: str
    active: bool
    created_at: datetime
    updated_at: datetime

class Document(BaseModel):
    id: uuid
    user_id: str
    file_name: str
    file_path: str
    uploaded_at: datetime
    updated_at: datetime

class AuthToken(BaseModel):
    user_id: uuid
    token: str
    created_at: datetime
    expires_at: datetime

class ChatHistory(BaseModel):
    user_id: uuid
    chat_id: uuid
    messages: List[dict]
    updated_at = datetime