from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class UrlResourceResponse(BaseModel):
    id: UUID
    original_url: str
    fetched_html: str | None = None
    parsed_markdown: str | None = None
    title: str | None = None
    description: str | None = None
    preview_image_url: str | None = None
    metadata_json: dict | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentBinaryResponse(BaseModel):
    sha256: str
    file_path: str
    file_type: str
    file_size: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentVersionResponse(BaseModel):
    id: UUID
    document_id: UUID
    version_number: int
    binary_id: str
    url_resource_id: UUID | None = None
    status: str
    status_message: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProcessingJobResponse(BaseModel):
    id: UUID
    document_version_id: UUID
    job_type: str
    status: str
    priority: int
    retry_count: int
    progress: int
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentStructureNodeResponse(BaseModel):
    id: UUID
    document_version_id: UUID
    node_category: str
    node_type: str
    parent_id: UUID | None = None
    order_index: int
    hierarchy_level: int
    page_start: int | None = None
    page_end: int | None = None
    char_start: int | None = None
    char_end: int | None = None
    line_start: int | None = None
    line_end: int | None = None
    language: str | None = None
    content_text: str
    content_markdown: str
    metadata_json: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


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
    document_version_id: UUID | None = None
    structure_node_id: UUID | None = None
    chunk_index: int
    page_number: int | None = None
    line_start: int | None = None
    line_end: int | None = None
    char_start: int | None = None
    char_end: int | None = None
    token_count: int | None = None
    char_count: int | None = None
    word_count: int | None = None
    hash: str | None = None
    parent_id: UUID | None = None
    heading: str | None = None
    metadata_json: dict | None = None
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


