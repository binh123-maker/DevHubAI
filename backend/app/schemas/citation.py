from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class CitationSchema(BaseModel):
    document_id: UUID | str | None = None
    document_name: str
    workspace_id: UUID | str | None = None
    workspace_name: str | None = None
    folder_id: UUID | str | None = None
    folder_name: str | None = None
    page_number: int | None = 1
    heading: str | None = None
    chunk_id: str | None = None
    chunk_index: int | None = 0
    semantic_unit_id: str | None = None
    confidence: float = 0.95  # Score between 0.0 and 1.0 (or percentage)
    confidence_level: str = "High"  # High (95-100), Medium (80-94), Fair (60-79), Low (<60)
    source_type: str = "pdf"  # pdf, markdown, docx, txt, web
    excerpt: str | None = None
    start_offset: int | None = None
    end_offset: int | None = None
    line_start: int | None = None
    line_end: int | None = None
    version: str | None = "v1"
    document_hash: str | None = None
    document_url: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class RetrievalMetadataSchema(BaseModel):
    documents_searched: int = 0
    chunks_retrieved: int = 0
    chunks_used: int = 0
    search_latency_ms: float = 0.0
    query_rewrite: str | None = None


class GenerationMetadataSchema(BaseModel):
    model: str = "Gemini 1.5 Pro (RAG)"
    generation_latency_ms: float = 0.0
    tokens_used: int = 0
    knowledge_scope: str = "global"


class EnrichedChatResponseSchema(BaseModel):
    answer: str
    sources: list[CitationSchema] = []
    retrieval_metadata: RetrievalMetadataSchema = Field(default_factory=RetrievalMetadataSchema)
    generation_metadata: GenerationMetadataSchema = Field(default_factory=GenerationMetadataSchema)
