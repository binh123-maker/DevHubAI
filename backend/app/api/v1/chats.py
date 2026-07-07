from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUser
from app.db.session import get_db
from app.schemas.chat import ChatCreate, ChatMessageCreate, ChatMessageResponse, ChatResponse, ChatUpdate
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


@router.get("/{chat_id}/messages", response_model=list[ChatMessageResponse])
def get_chat_messages(
    chat_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> list[ChatMessageResponse]:
    """Get all messages for a chat session."""
    try:
        return chat_service.get_chat_messages(db, current_user.id, chat_id)
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
@router.patch("/{chat_id}", response_model=ChatResponse)
def update_chat(
    chat_id: UUID,
    chat_in: ChatUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> ChatResponse:
    try:
        return chat_service.update_chat(db, current_user.id, chat_id, chat_in)
    except chat_service.ChatError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(
    chat_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    try:
        chat_service.delete_chat(db, current_user.id, chat_id)
    except chat_service.ChatError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
