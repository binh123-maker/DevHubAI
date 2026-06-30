"""
Document Processing Orchestrator.

Pipeline
--------
Upload → Extract Text → Markdown Conversion → Chunking → Store document_chunks

This service is intentionally synchronous and does NOT use any vector DB,
embeddings, LangChain, LlamaIndex, or AI frameworks.
It is invoked as a FastAPI BackgroundTask immediately after a file is saved.
"""
from __future__ import annotations

import logging
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.document import Document, DocumentChunk
from app.models.enums import DocumentStatus
from app.services.chunker import TextChunk, chunk_document
from app.services.processors.base import ExtractedDocument

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Dispatcher: pick the right extractor based on file_type
# ---------------------------------------------------------------------------

def _extract(file_path: Path, file_type: str) -> ExtractedDocument:
    ft = file_type.lower()

    if ft == "pdf":
        from app.services.processors.pdf_processor import extract_pdf
        return extract_pdf(file_path)

    if ft == "docx":
        from app.services.processors.docx_processor import extract_docx
        return extract_docx(file_path)

    if ft in ("txt", "md"):
        from app.services.processors.text_processor import extract_text
        return extract_text(file_path, ft)

    raise ValueError(f"Unsupported file type: {ft}")


# ---------------------------------------------------------------------------
# Chunk storage
# ---------------------------------------------------------------------------

def _store_chunks(db: Session, document_id: UUID, chunks: list[TextChunk]) -> None:
    db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()

    db_chunks = [
        DocumentChunk(
            document_id=document_id,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            content_markdown=chunk.content_markdown,
            page_number=chunk.page_number,
            line_start=chunk.line_start,
            line_end=chunk.line_end,
            heading=chunk.heading,
        )
        for chunk in chunks
    ]
    db.bulk_save_objects(db_chunks)
    db.commit()


# ---------------------------------------------------------------------------
# Public entry-point
# ---------------------------------------------------------------------------

def process_document(db: Session, document: Document) -> None:
    """
    Extract, chunk, and store content for a single Document.

    Marks `status=PROCESSING` at the start and `status=PROCESSED` on success,
    or `status=FAILED` if any error occurs.
    """
    # Mark as processing
    document.status = DocumentStatus.PROCESSING
    db.commit()

    try:
        file_path = Path(document.file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # 1. Extract
        extracted = _extract(file_path, document.file_type)

        if not extracted.pages:
            logger.warning("Document %s produced no pages after extraction.", document.id)

        # 2. Chunk
        chunks = chunk_document(extracted)
        logger.info("Document %s → %d chunks across %d pages.", document.id, len(chunks), len(extracted.pages))

        # 3. Store
        _store_chunks(db, document.id, chunks)

        # 4. Mark complete
        document.status = DocumentStatus.PROCESSED
        db.commit()

    except Exception as exc:
        logger.exception("Failed to process document %s: %s", document.id, exc)
        document.status = DocumentStatus.FAILED
        db.commit()
        # Don't re-raise — this runs in a BackgroundTask and we don't want to crash the app
