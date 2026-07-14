from uuid import UUID
from typing import Optional
import logging

logger = logging.getLogger(__name__)

from sqlalchemy import select, func, text, desc
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentChunk
from app.models.workspace import Workspace
from app.models.enums import ChatMode, DocumentStatus
from app.schemas.search import SearchResult


import sqlalchemy as sa
from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentChunk
from app.models.enums import ChatMode, DocumentStatus
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
    Search document_chunks using PostgreSQL Full Text Search, Metadata Search, and Code Search.
    Combines and re-ranks the streams with bonuses for matches across search methods.
    """
    if not query.strip():
        return []

    # Clean query terms
    terms = [t.strip().lower() for t in query.split() if len(t.strip()) > 2]
    if not terms:
        terms = [query.strip().lower()]

    # --- 1. KEYWORD SEARCH (FTS) ---
    tsquery = func.websearch_to_tsquery('simple', query)
    rank = func.ts_rank_cd(DocumentChunk.search_vector, tsquery).label("relevance_score")
    
    fts_stmt = (
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
            DocumentChunk.chunk_index,
        )
        .select_from(DocumentChunk)
        .join(Document, DocumentChunk.document_id == Document.id)
        .where(Document.user_id == user_id)
        .where(Document.status == DocumentStatus.PROCESSED)
        .where(DocumentChunk.search_vector.op("@@")(tsquery))
    )
    if workspace_id:
        fts_stmt = fts_stmt.where(Document.workspace_id == workspace_id)
    if folder_id:
        fts_stmt = fts_stmt.where(Document.folder_id == folder_id)
    if document_id:
        fts_stmt = fts_stmt.where(Document.id == document_id)
    if chat_mode == ChatMode.WEBSITE:
        fts_stmt = fts_stmt.where(Document.source_url.is_not(None))

    fts_results = db.execute(fts_stmt.limit(limit * 2)).mappings().all()

    # --- 2. METADATA SEARCH (Keywords / Tags in JSONB) ---
    meta_conds = []
    for term in terms:
        meta_conds.append(DocumentChunk.metadata_json['keywords'].astext.ilike(f"%{term}%"))
    
    meta_results = []
    if meta_conds:
        meta_stmt = (
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
                func.coalesce(DocumentChunk.id, DocumentChunk.id).label("relevance_score"),
                DocumentChunk.chunk_index,
            )
            .select_from(DocumentChunk)
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(Document.user_id == user_id)
            .where(Document.status == DocumentStatus.PROCESSED)
            .where(sa.or_(*meta_conds))
        )
        if workspace_id:
            meta_stmt = meta_stmt.where(Document.workspace_id == workspace_id)
        if folder_id:
            meta_stmt = meta_stmt.where(Document.folder_id == folder_id)
        if document_id:
            meta_stmt = meta_stmt.where(Document.id == document_id)
        if chat_mode == ChatMode.WEBSITE:
            meta_stmt = meta_stmt.where(Document.source_url.is_not(None))

        meta_results = db.execute(meta_stmt.limit(limit * 2)).mappings().all()

    # --- 3. CODE SEARCH (Functions, Classes, Imports, Routes, Database Tables) ---
    code_conds = []
    for term in terms:
        code_conds.extend([
            DocumentChunk.metadata_json['classes'].astext.ilike(f"%{term}%"),
            DocumentChunk.metadata_json['functions'].astext.ilike(f"%{term}%"),
            DocumentChunk.metadata_json['imports'].astext.ilike(f"%{term}%"),
            DocumentChunk.metadata_json['routes'].astext.ilike(f"%{term}%"),
            DocumentChunk.metadata_json['frameworks'].astext.ilike(f"%{term}%"),
            DocumentChunk.metadata_json['database_tables'].astext.ilike(f"%{term}%"),
        ])
    
    code_results = []
    if code_conds:
        code_stmt = (
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
                func.coalesce(DocumentChunk.id, DocumentChunk.id).label("relevance_score"),
                DocumentChunk.chunk_index,
            )
            .select_from(DocumentChunk)
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(Document.user_id == user_id)
            .where(Document.status == DocumentStatus.PROCESSED)
            .where(sa.or_(*code_conds))
        )
        if workspace_id:
            code_stmt = code_stmt.where(Document.workspace_id == workspace_id)
        if folder_id:
            code_stmt = code_stmt.where(Document.folder_id == folder_id)
        if document_id:
            code_stmt = code_stmt.where(Document.id == document_id)
        if chat_mode == ChatMode.WEBSITE:
            code_stmt = code_stmt.where(Document.source_url.is_not(None))

        code_results = db.execute(code_stmt.limit(limit * 2)).mappings().all()

    # --- 4. RANKING & MERGE LAYER ---
    merged_map = {}
    
    # Process FTS matches
    for row in fts_results:
        cid = row["chunk_id"]
        merged_map[cid] = {
            "row": row,
            "fts_score": float(row["relevance_score"]),
            "meta_match": False,
            "code_match": False
        }

    # Process Metadata matches
    for row in meta_results:
        cid = row["chunk_id"]
        if cid in merged_map:
            merged_map[cid]["meta_match"] = True
        else:
            merged_map[cid] = {
                "row": row,
                "fts_score": 0.0,
                "meta_match": True,
                "code_match": False
            }

    # Process Code matches
    for row in code_results:
        cid = row["chunk_id"]
        if cid in merged_map:
            merged_map[cid]["code_match"] = True
        else:
            merged_map[cid] = {
                "row": row,
                "fts_score": 0.0,
                "meta_match": False,
                "code_match": True
            }

    # Calculate combined score
    scored_results = []
    for cid, data in merged_map.items():
        score = data["fts_score"]
        if data["meta_match"]:
            score += 0.5
        if data["code_match"]:
            score += 0.8
            
        scored_results.append((score, data["row"]))

    # Sort descending by score
    scored_results.sort(key=lambda x: x[0], reverse=True)

    logger.info(f"[DEBUG RAG] Number of matched chunks: {len(scored_results)}")
    for i, (score, row) in enumerate(scored_results[:5]):
        logger.info(f"[DEBUG RAG] Top {i+1} chunk - Score: {score:.4f}, Heading: {row['heading']}")

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
            relevance_score=score,
            chunk_index=row["chunk_index"],
        )
        for score, row in scored_results[:limit]
    ]
