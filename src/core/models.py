from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, LargeBinary, Integer, func
from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY
import bcrypt
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(LargeBinary, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    chat_histories = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    tokens = relationship("AuthToken", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self.password)

    def generate_link(self):
        return f"http://localhost:8000/v1/login"


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    status = Column(String(32), nullable=False, default="pending", index=True)
    chunk_count = Column(Integer, nullable=True)
    error_message = Column(String(1024), nullable=True)
    index_name = Column(String(128), nullable=False, default="vector_db_index")
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="documents")

class ChatHistory(Base):
    __tablename__ = "chat_histories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    chat_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    messages = Column(ARRAY(JSONB), nullable=False, default=[])
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="chat_histories")

class AuthToken(Base):
    __tablename__ = "auth_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(512), unique=True, nullable=False, index=True)
    refresh_token = Column(String(512), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    refresh_expires_at = Column(DateTime(timezone=True), nullable=False)
    refresh_expired = Column(Boolean, nullable=False, default=False)

    user = relationship("User", back_populates="tokens")

class AgentRun(Base):
    """
    Represents one multi-agent execution (workflow).
    """
    __tablename__ = "agent_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    run_id = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    agents_involved = Column(ARRAY(String), nullable=False, default=[]) 
    input = Column(JSONB, nullable=False)   
    final_output = Column(JSONB, nullable=True)  
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True))


class AgentMessage(Base):
    """
    Stores individual agent-to-agent messages (like a chat log).
    """
    __tablename__ = "agent_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey("agent_runs.run_id", ondelete="CASCADE"), nullable=False)
    sender_agent = Column(String(100), nullable=False)  
    receiver_agent = Column(String(100), nullable=True)
    content = Column(JSONB, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    topic = Column(String(255), nullable=False)
    study_topics = Column(ARRAY(String), nullable=False, default=[])
    notes = Column(JSONB, nullable=True)
    test = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)