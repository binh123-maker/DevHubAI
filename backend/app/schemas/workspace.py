from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import MessageResponse

__all__ = ["MessageResponse", "WorkspaceCreate", "WorkspaceUpdate", "WorkspaceResponse", "FolderCreate", "FolderUpdate", "FolderResponse"]

class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    color: str = "#3B82F6"
    icon: str = "folder"


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    color: str | None = None
    icon: str | None = None


class WorkspaceResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    color: str
    icon: str
    document_count: int
    folder_count: int
    source_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FolderCreate(BaseModel):
    workspace_id: UUID
    parent_id: UUID | None = None
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    color: str = "#3B82F6"
    icon: str = "folder"


class FolderUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    color: str | None = None
    icon: str | None = None
    parent_id: UUID | None = None
    sort_order: int | None = None


class FolderResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    parent_id: UUID | None = None
    name: str
    description: str | None = None
    color: str
    icon: str
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
