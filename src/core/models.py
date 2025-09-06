from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, ARRAY, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID, INTEGER, CHAR, TEXT, TIMESTAMP
import bcrypt

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False)

    def set_password(self, password: str):
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    def verify_password(self, password: str) -> bool:
        if bcrypt.checkpw(password.encode('utf-8'), self.password):
            return True
        return False

class Document(Base):
    __tablename__ = 'documents'

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime, nullable=False)

class ChatHistory(Base):
    __tablename__ = 'chat_histories'

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    chat_id = Column(UUID(as_uuid=True), nullable=False)
    messages = Column(ARRAY(JSONB), nullable=False)
    updated_at = Column(DateTime, nullable=False)

class AuthToken(Base):
    __tablename__ = 'auth_tokens'

    id=Column(INTEGER, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    token = Column(String, unique=True, nullable=False)
    refresh_token = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    refresh_expires_at = Column(DateTime, nullable=False)
    refresh_expired = Column(Boolean, nullable=False, default=False)