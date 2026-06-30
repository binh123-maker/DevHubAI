from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUser
from app.db.session import get_db
from app.schemas.chat import ChatCreate, ChatMessageCreate, ChatMessageResponse, ChatResponse
from app.services import chat_service

router = APIRouter()

DbSession = Annotated[Session, Depends(get_db)]


@router.post("", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
def create_chat(
    chat_in: ChatCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> ChatResponse:
    """Create a new chat session."""
    return chat_service.create_chat(db, current_user.id, chat_in)


@router.get("", response_model=list[ChatResponse])
def get_chats(
    current_user: CurrentUser,
    db: DbSession,
    workspace_id: Optional[UUID] = Query(None),
) -> list[ChatResponse]:
    """List chats for the current user, optionally filtered by workspace_id."""
    return chat_service.get_chats(db, current_user.id, workspace_id)


@router.get("/{chat_id}", response_model=ChatResponse)
def get_chat(
    chat_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> ChatResponse:
    try:
        return chat_service.get_chat(db, current_user.id, chat_id)
    except chat_service.ChatError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{chat_id}/messages", response_model=ChatMessageResponse)
def send_message(
    chat_id: UUID,
    msg_in: ChatMessageCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> ChatMessageResponse:
    """Send a message to a chat, retrieve context, and get AI response."""
    try:
        return chat_service.send_message(db, current_user.id, chat_id, msg_in)
    except chat_service.ChatError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
