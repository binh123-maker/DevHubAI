from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ChatCreate(BaseModel):
    workspace_id: UUID | None = None
    folder_id: UUID | None = None
    document_id: UUID | None = None
    title: str = "Cuộc trò chuyện mới"
    chat_mode: str = "global"


class ChatUpdate(BaseModel):
    title: str | None = None
    is_favorite: bool | None = None


class ChatResponse(BaseModel):
    id: UUID
    workspace_id: UUID | None = None
    folder_id: UUID | None = None
    document_id: UUID | None = None
    title: str
    chat_mode: str
    is_favorite: bool
    status: str
    message_count: int
    created_at: datetime
    updated_at: datetime

    # Computed fields for UI
    workspace_name: str | None = None
    folder_name: str | None = None
    document_name: str | None = None
    last_message_content: str | None = None

    model_config = {"from_attributes": True}


class ChatMessageCreate(BaseModel):
    content: str = Field(min_length=1)


class CitationResponse(BaseModel):
    document_name: str
    source_type: str
    page_number: int | None = None
    line_start: int | None = None
    line_end: int | None = None
    heading: str | None = None
    url: str | None = None

    model_config = {"from_attributes": True}


class ChatMessageResponse(BaseModel):
    id: UUID
    chat_id: UUID
    role: str
    content: str
    created_at: datetime
    retrieved_chunk_count: int | None = None
    citations: list[CitationResponse] = []

    model_config = {"from_attributes": True}
