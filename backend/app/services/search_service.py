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
    Search document_chunks using PostgreSQL Full Text Search, Metadata Search, Heading/Filename Search,
    Substring ILIKE Fallback, and Multi-Factor Ranking.
    """
    if not query.strip():
        return []

    clean_query = query.strip()
    terms = [t.strip().lower() for t in clean_query.split() if len(t.strip()) > 1]
    if not terms:
        terms = [clean_query.lower()]

    merged_map = {}
    strategy_used = []

    def apply_filters(stmt):
        stmt = stmt.where(Document.user_id == user_id).where(Document.status == DocumentStatus.PROCESSED)
        if workspace_id:
            stmt = stmt.where(Document.workspace_id == workspace_id)
        if folder_id:
            stmt = stmt.where(Document.folder_id == folder_id)
        if document_id:
            stmt = stmt.where(Document.id == document_id)
        if chat_mode == ChatMode.WEBSITE:
            stmt = stmt.where(Document.source_url.is_not(None))
        return stmt

    # --- 1. KEYWORD SEARCH (FTS) ---
    try:
        tsquery = func.websearch_to_tsquery('simple', clean_query)
        rank = func.ts_rank_cd(DocumentChunk.search_vector, tsquery).label("relevance_score")
        
        fts_stmt = select(
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
        ).select_from(DocumentChunk).join(Document, DocumentChunk.document_id == Document.id).where(
            DocumentChunk.search_vector.op("@@")(tsquery)
        )
        fts_stmt = apply_filters(fts_stmt)
        fts_results = db.execute(fts_stmt.limit(limit * 2)).mappings().all()

        if fts_results:
            strategy_used.append("FTS")
            for row in fts_results:
                cid = row["chunk_id"]
                merged_map[cid] = {
                    "row": row,
                    "fts_score": float(row["relevance_score"] or 0.0),
                    "meta_match": False,
                    "code_match": False,
                    "heading_match": False,
                    "filename_match": False,
                    "ilike_match": False,
                }
    except Exception as err:
        logger.warning(f"[RAG RECOVERY] FTS query failed: {err}")

    # --- 2. METADATA & CODE SEARCH ---
    meta_conds = []
    code_conds = []
    for term in terms:
        meta_conds.append(DocumentChunk.metadata_json['keywords'].astext.ilike(f"%{term}%"))
        code_conds.extend([
            DocumentChunk.metadata_json['classes'].astext.ilike(f"%{term}%"),
            DocumentChunk.metadata_json['functions'].astext.ilike(f"%{term}%"),
            DocumentChunk.metadata_json['imports'].astext.ilike(f"%{term}%"),
            DocumentChunk.metadata_json['routes'].astext.ilike(f"%{term}%"),
        ])
    
    if meta_conds or code_conds:
        all_conds = meta_conds + code_conds
        meta_stmt = select(
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
        ).select_from(DocumentChunk).join(Document, DocumentChunk.document_id == Document.id).where(sa.or_(*all_conds))
        meta_stmt = apply_filters(meta_stmt)
        meta_results = db.execute(meta_stmt.limit(limit * 2)).mappings().all()

        if meta_results:
            strategy_used.append("Metadata/Code")
            for row in meta_results:
                cid = row["chunk_id"]
                if cid in merged_map:
                    merged_map[cid]["meta_match"] = True
                    merged_map[cid]["code_match"] = True
                else:
                    merged_map[cid] = {
                        "row": row,
                        "fts_score": 0.0,
                        "meta_match": True,
                        "code_match": True,
                        "heading_match": False,
                        "filename_match": False,
                        "ilike_match": False,
                    }

    # --- 3. HEADING & FILENAME SEARCH (Part 16 Recovery) ---
    head_file_conds = []
    for term in terms:
        head_file_conds.extend([
            DocumentChunk.heading.ilike(f"%{term}%"),
            Document.file_name.ilike(f"%{term}%"),
            Document.title.ilike(f"%{term}%"),
        ])
    if head_file_conds:
        head_stmt = select(
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
        ).select_from(DocumentChunk).join(Document, DocumentChunk.document_id == Document.id).where(sa.or_(*head_file_conds))
        head_stmt = apply_filters(head_stmt)
        head_results = db.execute(head_stmt.limit(limit * 2)).mappings().all()

        if head_results:
            strategy_used.append("Heading/Filename")
            for row in head_results:
                cid = row["chunk_id"]
                if cid in merged_map:
                    merged_map[cid]["heading_match"] = True
                    merged_map[cid]["filename_match"] = True
                else:
                    merged_map[cid] = {
                        "row": row,
                        "fts_score": 0.0,
                        "meta_match": False,
                        "code_match": False,
                        "heading_match": True,
                        "filename_match": True,
                        "ilike_match": False,
                    }

    # --- 4. SUBSTRING ILIKE FALLBACK (Part 16 Recovery) ---
    if not merged_map:
        ilike_conds = [DocumentChunk.content.ilike(f"%{term}%") for term in terms]
        if ilike_conds:
            ilike_stmt = select(
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
            ).select_from(DocumentChunk).join(Document, DocumentChunk.document_id == Document.id).where(sa.or_(*ilike_conds))
            ilike_stmt = apply_filters(ilike_stmt)
            ilike_results = db.execute(ilike_stmt.limit(limit * 2)).mappings().all()

            if ilike_results:
                strategy_used.append("ILIKE Substring Fallback")
                for row in ilike_results:
                    cid = row["chunk_id"]
                    merged_map[cid] = {
                        "row": row,
                        "fts_score": 0.0,
                        "meta_match": False,
                        "code_match": False,
                        "heading_match": False,
                        "filename_match": False,
                        "ilike_match": True,
                    }

    # --- 5. WORKSPACE CONTEXT FALLBACK (If 0 matched chunks but docs exist) ---
    if not merged_map:
        recent_stmt = select(
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
        ).select_from(DocumentChunk).join(Document, DocumentChunk.document_id == Document.id)
        recent_stmt = apply_filters(recent_stmt).order_by(DocumentChunk.created_at.desc())
        recent_results = db.execute(recent_stmt.limit(5)).mappings().all()
        if recent_results:
            strategy_used.append("Recent Workspace Chunks Fallback")
            for row in recent_results:
                cid = row["chunk_id"]
                merged_map[cid] = {
                    "row": row,
                    "fts_score": 0.0,
                    "meta_match": False,
                    "code_match": False,
                    "heading_match": False,
                    "filename_match": False,
                    "ilike_match": False,
                }

    # --- 6. MULTI-FACTOR RANKING & SCORING (Part 25) ---
    scored_results = []
    for cid, data in merged_map.items():
        score = data["fts_score"]
        if data["meta_match"]:
            score += 0.5
        if data["code_match"]:
            score += 0.8
        if data["heading_match"]:
            score += 0.6
        if data["filename_match"]:
            score += 0.4
        if data["ilike_match"]:
            score += 0.3
        
        # Chunk quality bonus: penalize extremely short or noisy chunks
        content_len = len((data["row"]["content"] or "").strip())
        if content_len > 100:
            score += 0.2
            
        scored_results.append((score, data["row"]))

    scored_results.sort(key=lambda x: x[0], reverse=True)

    strategy_str = ", ".join(strategy_used) if strategy_used else "None"
    logger.info(f"[RAG RECOVERY & DIAGNOSTIC] Matched Chunks: {len(scored_results)} | Strategies: {strategy_str}")

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
