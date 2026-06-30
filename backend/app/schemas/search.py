from uuid import UUID
from pydantic import BaseModel


class SearchResult(BaseModel):
    chunk_id: UUID
    document_id: UUID
    document_name: str
    content: str
    page_number: int | None = None
    line_start: int | None = None
    line_end: int | None = None
    relevance_score: float

    model_config = {"from_attributes": True}
