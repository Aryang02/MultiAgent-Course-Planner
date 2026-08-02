import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.exceptions import NotFoundError
from src.auth.auth import get_user
from src.core.models import User
from src.database.db import get_db
from src.repositories import ChatRepository
from src.serializers.backend import ChatListResponse, ChatResponse, ChatSummary, NewChatResponse

router = APIRouter(prefix="/v1", tags=["chats"])


@router.get("/chats", response_model=ChatListResponse)
def list_chats(
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
) -> ChatListResponse:
    chats = ChatRepository(db)
    user_chats = chats.list_for_user(user.id)
    return ChatListResponse(
        chats=[
            ChatSummary(
                chat_id=chat.chat_id,
                message_count=len(chat.messages or []),
                updated_at=chat.updated_at,
            )
            for chat in user_chats
        ]
    )


@router.get("/chats/{chat_id}", response_model=ChatResponse)
def get_chat(
    chat_id: uuid.UUID,
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
) -> ChatResponse:
    chats = ChatRepository(db)
    chat = chats.get_by_chat_id(user.id, chat_id)
    if not chat:
        raise NotFoundError("Chat not found")
    return ChatResponse(
        chat_id=chat.chat_id,
        messages=chat.messages or [],
        updated_at=chat.updated_at,
    )


@router.post("/chats", response_model=NewChatResponse, status_code=201)
def new_chat(
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
) -> NewChatResponse:
    chats = ChatRepository(db)
    chat = chats.create_chat(user.id)
    db.commit()
    return NewChatResponse(chat_id=chat.chat_id)
