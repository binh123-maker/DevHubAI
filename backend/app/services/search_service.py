from uuid import UUID
from typing import Optional

from sqlalchemy import select, func, text, desc
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentChunk
from app.models.workspace import Workspace
from app.schemas.search import SearchResult


def search_documents(
    db: Session,
    user_id: UUID,
    query: str,
    workspace_id: Optional[UUID] = None,
    limit: int = 10,
) -> list[SearchResult]:
    """
    Search document_chunks using PostgreSQL Full Text Search.
    Filters by user_id to ensure security. Optionally filters by workspace_id.
    """
    if not query.strip():
        return []

    # Use plainto_tsquery for simple search queries (handles spaces, quotes gracefully)
    tsquery = func.plainto_tsquery('simple', query)
    
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

    # Order by rank and limit
    stmt = stmt.order_by(desc(rank)).limit(limit)

    results = db.execute(stmt).mappings().all()

    return [
        SearchResult(
            chunk_id=row["chunk_id"],
            document_id=row["document_id"],
            document_name=row["document_name"],
            content=row["content"],
            page_number=row["page_number"],
            line_start=row["line_start"],
            line_end=row["line_end"],
            relevance_score=float(row["relevance_score"]),
        )
        for row in results
    ]
