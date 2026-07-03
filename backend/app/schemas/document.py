from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    folder_id: UUID | None = None
    title: str
    description: str | None = None
    file_name: str
    file_type: str
    file_size: int
    status: str
    view_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChunkResponse(BaseModel):
    id: UUID
    document_id: UUID
    chunk_index: int
    page_number: int | None = None
    line_start: int | None = None
    line_end: int | None = None
    heading: str | None = None
    content: str
    content_markdown: str
    created_at: datetime

    model_config = {"from_attributes": True}


class BulkDeleteRequest(BaseModel):
    document_ids: list[UUID]


class DocumentUpdateRequest(BaseModel):
    title: str
    description: str | None = None

class UrlUploadRequest(BaseModel):
    workspace_id: UUID
    folder_id: UUID | None = None
    url: str
    title: str | None = None
    description: str | None = None

