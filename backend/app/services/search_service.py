from uuid import UUID
from typing import Optional
import logging

logger = logging.getLogger(__name__)

from sqlalchemy import select, func, text, desc
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentChunk
from app.models.workspace import Workspace
from app.models.enums import ChatMode
from app.schemas.search import SearchResult


def search_documents(
    db: Session,
    user_id: UUID,
    query: str,
    workspace_id: Optional[UUID] = None,
    folder_id: Optional[UUID] = None,
    document_id: Optional[UUID] = None,
    chat_mode: Optional[ChatMode] = None,
    limit: int = 10,
) -> list[SearchResult]:
    """
    Search document_chunks using PostgreSQL Full Text Search.
    Filters by user_id to ensure security. Optionally filters by workspace_id.
    """
    if not query.strip():
        return []

    # Use websearch_to_tsquery for natural language search
    tsquery = func.websearch_to_tsquery('simple', query)
    
    try:
        parsed_query = db.execute(select(func.websearch_to_tsquery('simple', query))).scalar()
        logger.info(f"[DEBUG RAG] Parsed tsquery: {parsed_query}")
    except Exception as e:
        logger.error(f"[DEBUG RAG] Failed to parse query: {e}")
    
    # Calculate rank using ts_rank_cd (Cover Density Ranking)
    rank = func.ts_rank_cd(DocumentChunk.search_vector, tsquery).label("relevance_score")

    # Base query
    stmt = (
        select(
            DocumentChunk.id.label("chunk_id"),
            Document.id.label("document_id"),
            Document.file_name.label("document_name"),
            DocumentChunk.content,
            DocumentChunk.page_number,
            DocumentChunk.line_start,
            DocumentChunk.line_end,
            DocumentChunk.heading,
            Document.source_url,
            rank,
        )
        .select_from(DocumentChunk)
        .join(Document, DocumentChunk.document_id == Document.id)
        .where(Document.user_id == user_id)  # Security enforcement
        .where(DocumentChunk.search_vector.op("@@")(tsquery))
    )

    # Apply workspace filter if provided
    if workspace_id:
        stmt = stmt.where(Document.workspace_id == workspace_id)
    if folder_id:
        stmt = stmt.where(Document.folder_id == folder_id)
    if document_id:
        stmt = stmt.where(Document.id == document_id)
        
    if chat_mode == ChatMode.WEBSITE:
        stmt = stmt.where(Document.source_url.is_not(None))

    # Order by rank and limit
    stmt = stmt.order_by(desc(rank)).limit(limit)

    results = db.execute(stmt).mappings().all()

    logger.info(f"[DEBUG RAG] Number of matched chunks: {len(results)}")
    for i, row in enumerate(results[:5]):
        logger.info(f"[DEBUG RAG] Top {i+1} chunk - Score: {float(row['relevance_score']):.4f}, Heading: {row['heading']}")

    return [
        SearchResult(
            chunk_id=row["chunk_id"],
            document_id=row["document_id"],
            document_name=row["document_name"],
            content=row["content"],
            page_number=row["page_number"],
            line_start=row["line_start"],
            line_end=row["line_end"],
            heading=row["heading"],
            source_url=row["source_url"],
            relevance_score=float(row["relevance_score"]),
        )
        for row in results
    ]
