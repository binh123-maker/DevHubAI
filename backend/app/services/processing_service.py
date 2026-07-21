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
    from app.services.ocr_pipeline import perform_ocr

    if ft in ("png", "jpg", "jpeg", "gif", "webp", "tiff", "bmp"):
        return perform_ocr(file_path)

    if ft == "pdf":
        from app.services.processors.pdf_processor import extract_pdf
        extracted = extract_pdf(file_path)
        # Check if scanned PDF
        total_text_len = sum(len(p.raw_text) for p in extracted.pages)
        if total_text_len < 50:
            logger.info("PDF %s appears scanned (len=%d). Triggering OCR...", file_path, total_text_len)
            return perform_ocr(file_path)
        return extracted

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

def _store_chunks(
    db: Session,
    document_id: UUID,
    version_id: UUID | None = None,
    chunk_dicts: list[dict] = []
) -> None:
    from app.services.metadata_builder import build_metadata

    if version_id:
        db.query(DocumentChunk).filter(DocumentChunk.document_version_id == version_id).delete()
    else:
        db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()

    db_chunks = []
    for c in chunk_dicts:
        is_code = False
        language = None
        
        # Resolve language if node is present
        node_id = c.get("structure_node_id")
        if node_id:
            from app.models.document import DocumentStructureNode
            node = db.get(DocumentStructureNode, node_id)
            if node:
                is_code = (node.node_category == "code")
                language = node.language

        c_metadata = c.get("metadata_json")
        if c_metadata is None:
            c_metadata = build_metadata(c["content"], is_code, language)

        db_chunks.append(
            DocumentChunk(
                document_id=document_id,
                document_version_id=version_id,
                structure_node_id=c["structure_node_id"],
                chunk_index=c["chunk_index"],
                content=c["content"],
                content_markdown=c["content_markdown"],
                page_number=c["page_number"],
                line_start=c["line_start"],
                line_end=c["line_end"],
                char_start=c["char_start"],
                char_end=c["char_end"],
                token_count=c["token_count"],
                char_count=c["char_count"],
                word_count=c["word_count"],
                hash=c["hash"],
                heading=c["heading"],
                metadata_json=c_metadata,
            )
        )

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

        # 2. Chunk (Legacy fallback)
        chunks = chunk_document(extracted)
        logger.info("Document %s → %d chunks across %d pages.", document.id, len(chunks), len(extracted.pages))

        # 3. Store
        legacy_dicts = [
            {
                "structure_node_id": None,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "content_markdown": chunk.content_markdown,
                "page_number": chunk.page_number,
                "line_start": chunk.line_start,
                "line_end": chunk.line_end,
                "char_start": None,
                "char_end": None,
                "token_count": int(len(chunk.content) / 4),
                "char_count": len(chunk.content),
                "word_count": len(chunk.content.split()),
                "hash": hashlib.sha256(chunk.content.encode('utf-8')).hexdigest(),
                "heading": chunk.heading,
            }
            for chunk in chunks
        ]
        _store_chunks(db, document.id, None, legacy_dicts)

        # 4. Index FTS
        from app.services.index_builder import PostgresIndexBuilder
        # Update FTS vector for legacy fallback by matching document_id (since version_id is None)
        from sqlalchemy import update, func
        db.execute(
            update(DocumentChunk)
            .where(DocumentChunk.document_id == document.id)
            .values(search_vector=func.to_tsvector('simple', DocumentChunk.content))
        )
        db.commit()

        # 5. Mark complete
        document.status = DocumentStatus.PROCESSED
        db.commit()

    except Exception as exc:
        logger.exception("Failed to process document %s: %s", document.id, exc)
        document.status = DocumentStatus.FAILED
        db.commit()
        # Don't re-raise — this runs in a BackgroundTask and we don't want to crash the app


class JobCancelledException(Exception):
    pass


def execute_processing_job(db: Session, job_id: UUID) -> None:
    """
    Asynchronously run parser, chunker, and indexer with support for cancellation, progress tracking, and retry options.
    """
    from sqlalchemy import select
    from app.models.document import ProcessingJob, DocumentStructureNode

    # 1. Fetch the job
    job = db.scalar(select(ProcessingJob).where(ProcessingJob.id == job_id))
    if not job:
        logger.error("Processing job %s not found.", job_id)
        return

    # If already cancelled, do not process
    if job.status == "cancelled":
        logger.info("Job %s is already cancelled. Skipping.", job_id)
        return

    # 2. Update job status to running
    job.status = "running"
    job.progress = 10
    version = job.document_version
    document = version.document
    binary = version.binary

    version.status = DocumentStatus.PROCESSING
    document.status = DocumentStatus.PROCESSING
    db.commit()

    try:
        # Check cancellation
        db.refresh(job)
        if job.status == "cancelled":
            raise JobCancelledException()

        file_path = Path(binary.file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # 3. Extract (progress = 30)
        job.progress = 30
        db.commit()

        extracted = _extract(file_path, binary.file_type)

        # Check cancellation
        db.refresh(job)
        if job.status == "cancelled":
            raise JobCancelledException()

        if not extracted.pages:
            logger.warning("Document version %s produced no pages after extraction.", version.id)

        # 4. Parse Structure Tree (progress = 50)
        job.progress = 50
        db.commit()

        from app.services.structure_parser import parse_structure
        from app.services.metadata_builder import build_metadata
        
        # Delete old structure nodes if they exist
        db.query(DocumentStructureNode).filter(DocumentStructureNode.document_version_id == version.id).delete()
        
        from app.services.document_structure.document_structure_analyzer import analyze_document_structure
        node_dicts = analyze_document_structure(version.id, file_path, binary.file_type)
        
        nodes = []
        for d in node_dicts:
            nodes.append(
                DocumentStructureNode(
                    id=d["id"],
                    document_version_id=d["document_version_id"],
                    node_category=d["node_category"],
                    node_type=d["node_type"],
                    parent_id=d["parent_id"],
                    order_index=d["order_index"],
                    hierarchy_level=d["hierarchy_level"],
                    page_start=d["page_start"],
                    page_end=d["page_end"],
                    char_start=d["char_start"],
                    char_end=d["char_end"],
                    line_start=d["line_start"],
                    line_end=d["line_end"],
                    language=d["language"],
                    content_text=d["content_text"],
                    content_markdown=d["content_markdown"],
                    metadata_json=d["metadata_json"]
                )
            )
            
        db_session = Session.object_session(job) if hasattr(Session, 'object_session') else db
        db_session.add_all(nodes)
        db_session.commit()

        # Check cancellation
        db.refresh(job)
        if job.status == "cancelled":
            raise JobCancelledException()

        # 5. Chunk from Structure (progress = 70)
        job.progress = 70
        db.commit()

        fallback_used = False
        try:
            # ── Semantic Pipeline (Production) ────────────────────────────────
            from app.services.pipeline.pipeline_context import PipelineContext
            from app.services.pipeline.pipeline_profile import PipelineProfile
            from app.services.pipeline.semantic_pipeline import SemanticPipeline

            pipe_ctx = PipelineContext(
                document=document,
                document_version=version,
                nodes=nodes,
            )
            pipeline = SemanticPipeline(profile=PipelineProfile.production())
            pipeline.execute(pipe_ctx)

            chunks = pipe_ctx.db_chunks
            avg_tok = sum(c["token_count"] for c in chunks) / len(chunks) if chunks else 0
            logger.info(
                "SemanticPipeline: Document %s | Nodes: %d | Chunks: %d | Avg Tokens: %.2f | Health: %.2f | Stages: %d",
                document.id, len(nodes), len(chunks), avg_tok,
                pipe_ctx.pipeline_health, len(pipe_ctx.stage_timings),
            )

        except Exception as exc:
            logger.exception("SemanticPipeline failed. Falling back to legacy chunker: %s", exc)
            fallback_used = True
            from app.services.chunk_builder import build_chunks_from_structure
            chunks = build_chunks_from_structure(nodes)
            logger.info("Legacy fallback: Document %s | Chunks: %d | Fallback Used: True", document.id, len(chunks))

        # Check cancellation
        db.refresh(job)
        if job.status == "cancelled":
            raise JobCancelledException()

        logger.info("Document version %s → %d chunks.", version.id, len(chunks))

        # 6. Store (progress = 85)
        job.progress = 85
        db.commit()

        _store_chunks(db, document.id, version.id, chunks)

        # Check cancellation
        db.refresh(job)
        if job.status == "cancelled":
            raise JobCancelledException()

        # 7. Index Chunks (progress = 95)
        job.progress = 95
        db.commit()

        from app.services.index_builder import PostgresIndexBuilder
        PostgresIndexBuilder().index_version_chunks(db, version.id)

        # Check cancellation
        db.refresh(job)
        if job.status == "cancelled":
            raise JobCancelledException()

        # 8. Complete (progress = 100)
        job.status = "completed"
        job.progress = 100
        version.status = DocumentStatus.PROCESSED
        document.status = DocumentStatus.PROCESSED
        db.commit()

    except JobCancelledException:
        logger.info("Job %s was cancelled during execution.", job_id)
        db.rollback()
        # Retrieve again to change status
        job = db.scalar(select(ProcessingJob).where(ProcessingJob.id == job_id))
        if job:
            job.status = "cancelled"
            version = job.document_version
            document = version.document
            version.status = DocumentStatus.FAILED
            document.status = DocumentStatus.FAILED
            db.commit()

    except Exception as exc:
        logger.exception("Failed to execute processing job %s: %s", job_id, exc)
        db.rollback()
        job = db.scalar(select(ProcessingJob).where(ProcessingJob.id == job_id))
        if job:
            if job.retry_count < 3:
                job.retry_count += 1
                job.status = "pending"
                job.error_message = f"Retry {job.retry_count} failed: {str(exc)}"
                db.commit()
                # Trigger retry asynchronously
                from app.services.document_service import trigger_job_processing
                trigger_job_processing(job.id)
            else:
                job.status = "failed"
                job.error_message = str(exc)
                version = job.document_version
                document = version.document
                version.status = DocumentStatus.FAILED
                document.status = DocumentStatus.FAILED
                db.commit()


