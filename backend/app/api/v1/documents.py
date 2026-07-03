from typing import Annotated, Optional
from uuid import UUID

from typing import Annotated, Optional
from fastapi import File, Form, UploadFile

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUser
from app.db.session import get_db
from app.schemas.common import MessageResponse
from app.schemas.document import BulkDeleteRequest, ChunkResponse, DocumentResponse, DocumentUpdateRequest, UrlUploadRequest
from app.services import document_service

router = APIRouter()

DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    current_user: CurrentUser,
    db: DbSession,
    workspace_id: UUID = None,
    folder_id: Optional[UUID] = None,
) -> list[DocumentResponse]:
    try:
        return document_service.list_documents(db, current_user.id, workspace_id, folder_id)
    except Exception as e:
        from app.services.workspace_service import WorkspaceError
        if isinstance(e, WorkspaceError):
            raise HTTPException(status_code=e.status_code, detail=e.message)
        raise

@router.post("/upload-url", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document_url(
    payload: UrlUploadRequest,
    current_user: CurrentUser,
    db: DbSession,
    background_tasks: BackgroundTasks,
) -> DocumentResponse:
    try:
        document = document_service.upload_document_from_url(
            db=db,
            user_id=current_user.id,
            workspace_id=payload.workspace_id,
            folder_id=payload.folder_id,
            url=payload.url,
            title=payload.title,
            description=payload.description,
        )
        # Trigger download & processing asynchronously
        background_tasks.add_task(document_service.download_and_process_url, document.id, payload.url)
        return document
    except document_service.DocumentError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        from app.services.workspace_service import WorkspaceError
        from app.services.folder_service import FolderError
        if isinstance(e, (WorkspaceError, FolderError)):
            raise HTTPException(status_code=e.status_code, detail=e.message)
        raise

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    current_user: CurrentUser,
    db: DbSession,
    background_tasks: BackgroundTasks,
    workspace_id: UUID = Form(...),
    folder_id: Optional[UUID] = Form(None),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
) -> DocumentResponse:
    try:
        document = document_service.upload_document(
            db=db,
            user_id=current_user.id,
            workspace_id=workspace_id,
            folder_id=folder_id,
            file=file,
            title=title,
            description=description,
        )
        # Trigger processing asynchronously
        background_tasks.add_task(document_service.trigger_processing_task, document.id)
        return document
    except document_service.DocumentError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        from app.services.workspace_service import WorkspaceError
        from app.services.folder_service import FolderError
        if isinstance(e, (WorkspaceError, FolderError)):
            raise HTTPException(status_code=e.status_code, detail=e.message)
        raise


@router.delete("/bulk", response_model=MessageResponse)
def bulk_delete_documents(
    payload: BulkDeleteRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> MessageResponse:
    """Delete multiple documents by ID. Documents not owned by the user are silently skipped."""
    count = document_service.bulk_delete_documents(db, current_user.id, payload.document_ids)
    return MessageResponse(message=f"{count} document(s) deleted successfully")


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> DocumentResponse:
    try:
        return document_service.get_owned_document(db, current_user.id, document_id)
    except document_service.DocumentError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{document_id}/chunks", response_model=list[ChunkResponse])
def get_document_chunks(
    document_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> list[ChunkResponse]:
    """Return all text chunks extracted from this document."""
    try:
        return document_service.get_document_chunks(db, current_user.id, document_id)
    except document_service.DocumentError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: UUID,
    payload: DocumentUpdateRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> DocumentResponse:
    """Rename and/or update the description of a document."""
    try:
        return document_service.update_document(
            db,
            current_user.id,
            document_id,
            payload.title,
            payload.description,
        )
    except document_service.DocumentError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{document_id}", response_model=MessageResponse)
def delete_document(
    document_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> MessageResponse:
    try:
        document_service.delete_document(db, current_user.id, document_id)
        return MessageResponse(message="Document deleted successfully")
    except document_service.DocumentError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
