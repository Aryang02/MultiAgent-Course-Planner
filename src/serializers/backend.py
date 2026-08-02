from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class ErrorResponse(BaseModel):
    detail: str
    request_id: str | None = None


class LogoutRequest(BaseModel):
    refresh_token: str


class RefreshRequest(BaseModel):
    refresh_token: str


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class UploadResponse(BaseModel):
    task_id: str
    detail: str
    files_uploaded: int
    document_ids: list[UUID]
    status: str = "pending"


class DocumentResponse(BaseModel):
    id: UUID
    file_name: str
    status: str
    chunk_count: int | None = None
    error_message: str | None = None
    index_name: str
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]


class GenerateRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    chat_id: UUID


class GenerateResponse(BaseModel):
    task_id: str
    status: str = "pending"
    message: str = "Generation task accepted"


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: dict[str, Any] | None = None
    error: str | None = None


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime | None = None


class ChatResponse(BaseModel):
    chat_id: UUID
    messages: list[dict[str, Any]]
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ChatSummary(BaseModel):
    chat_id: UUID
    message_count: int
    updated_at: datetime | None = None


class ChatListResponse(BaseModel):
    chats: list[ChatSummary]


class NewChatResponse(BaseModel):
    chat_id: UUID


class StudyPlanResponse(BaseModel):
    id: UUID
    topic: str
    study_topics: list[str]
    notes: dict[str, Any] | None = None
    test: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StudyPlanListResponse(BaseModel):
    plans: list[StudyPlanResponse]


class HealthResponse(BaseModel):
    status: str


class ReadyResponse(BaseModel):
    status: str
    database: str
    redis: str
