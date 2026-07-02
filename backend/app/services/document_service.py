import logging
import uuid
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import Document, DocumentChunk
from app.models.enums import DocumentStatus
from app.services.folder_service import get_owned_folder
from app.services.workspace_service import get_owned_workspace

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(settings.upload_dir)
MAX_FILE_SIZE = settings.max_upload_size_mb * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
}

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class DocumentError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def validate_file(file: UploadFile) -> None:
    # Check extension
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise DocumentError(
            f"File extension not allowed. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}",
            status_code=415,
        )

    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise DocumentError(
            f"File content type not allowed. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}",
            status_code=415,
        )


def get_owned_document(db: Session, user_id: UUID, document_id: UUID) -> Document:
    document = db.scalar(
        select(Document).where(Document.id == document_id, Document.user_id == user_id)
    )
    if not document:
        raise DocumentError("Document not found", status_code=404)
    return document


def list_documents(db: Session, user_id: UUID, workspace_id: UUID, folder_id: UUID | None = None) -> list[Document]:
    # Validate workspace ownership
    get_owned_workspace(db, user_id, workspace_id)
    
    query = select(Document).where(Document.workspace_id == workspace_id)
    if folder_id:
        query = query.where(Document.folder_id == folder_id)
    else:
        query = query.where(Document.folder_id.is_(None))
        
    return list(db.scalars(query.order_by(Document.created_at.desc())))


def upload_document(
    db: Session,
    user_id: UUID,
    workspace_id: UUID,
    folder_id: UUID | None,
    file: UploadFile,
    title: str | None,
    description: str | None,
) -> Document:
    # 1. Validate ownership
    get_owned_workspace(db, user_id, workspace_id)
    if folder_id:
        folder = get_owned_folder(db, user_id, folder_id)
        if folder.workspace_id != workspace_id:
            raise DocumentError("Folder does not belong to the specified workspace", status_code=400)

    # 2. Validate file type
    validate_file(file)

    # 3. Create unique file path
    file_id = uuid.uuid4()
    ext = Path(file.filename or "").suffix.lower()
    saved_filename = f"{file_id}{ext}"
    workspace_dir = UPLOAD_DIR / str(workspace_id)
    workspace_dir.mkdir(parents=True, exist_ok=True)
    file_path = workspace_dir / saved_filename

    # 4. Save file and get size
    file_size = 0
    with open(file_path, "wb") as buffer:
        while chunk := file.file.read(8192):
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                file_path.unlink(missing_ok=True)
                raise DocumentError(f"File too large. Maximum size is {MAX_FILE_SIZE / (1024 * 1024):.0f}MB", status_code=413)
            buffer.write(chunk)

    # 5. Save to database
    doc_title = title.strip() if title else (file.filename or "Untitled")
    
    document = Document(
        id=file_id,
        user_id=user_id,
        workspace_id=workspace_id,
        folder_id=folder_id,
        title=doc_title,
        description=description.strip() if description else None,
        file_name=file.filename or "unknown",
        file_type=ext.lstrip("."),
        file_size=file_size,
        file_path=str(file_path),
        status=DocumentStatus.UPLOADING,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def trigger_processing(db: Session, document: Document) -> None:
    """Run the document processing pipeline synchronously (called from BackgroundTask)."""
    from app.services.processing_service import process_document  # local import to avoid circular
    process_document(db, document)


def get_document_chunks(db: Session, user_id: UUID, document_id: UUID) -> list[DocumentChunk]:
    """Return all chunks for a document the user owns, ordered by chunk_index."""
    document = get_owned_document(db, user_id, document_id)
    return (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document.id)
        .order_by(DocumentChunk.chunk_index)
        .all()
    )


def delete_document(db: Session, user_id: UUID, document_id: UUID) -> None:
    document = get_owned_document(db, user_id, document_id)
    
    # Delete physical file
    file_path = Path(document.file_path)
    if file_path.exists():
        file_path.unlink(missing_ok=True)
        
    db.delete(document)
    db.commit()


def update_document(
    db: Session,
    user_id: UUID,
    document_id: UUID,
    title: str,
    description: str | None,
) -> Document:
    """Rename (and optionally redescribe) a document the user owns."""
    document = get_owned_document(db, user_id, document_id)

    title = title.strip()
    if not title:
        raise DocumentError("Title cannot be empty", status_code=422)
    if len(title) > 255:
        raise DocumentError("Title must be 255 characters or fewer", status_code=422)

    document.title = title
    document.description = description.strip() if description else None

    db.commit()
    db.refresh(document)
    return document


def bulk_delete_documents(db: Session, user_id: UUID, document_ids: list[UUID]) -> int:
    """Delete multiple documents owned by user_id. Returns the count of deleted documents."""
    count = 0
    for document_id in document_ids:
        try:
            delete_document(db, user_id, document_id)
            count += 1
        except DocumentError:
            # Skip documents that don't exist or don't belong to the user
            pass
    return count
