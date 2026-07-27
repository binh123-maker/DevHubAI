import re
from typing import Any, Dict, List, Tuple
from uuid import UUID
from app.schemas.citation import CitationSchema


class CitationService:
    @staticmethod
    def calculate_confidence(score: float) -> Tuple[float, str]:
        """
        Converts similarity score into a normalized float (0.0 to 1.0)
        and returns confidence label:
        High (95-100), Medium (80-94), Fair (60-79), Low (<60)
        """
        norm_score = max(0.0, min(1.0, score if score <= 1.0 else score / 100.0))
        percentage = norm_score * 100.0

        if percentage >= 95.0:
            level = "High"
        elif percentage >= 80.0:
            level = "Medium"
        elif percentage >= 60.0:
            level = "Fair"
        else:
            level = "Low"

        return norm_score, level

    @staticmethod
    def extract_excerpt(text: str, max_words: int = 40) -> str:
        """Extracts a clean, representative excerpt from chunk content."""
        if not text:
            return "Trích đoạn từ tài liệu chỉ mục RAG..."
        clean = re.sub(r"\s+", " ", text).strip()
        words = clean.split(" ")
        if len(words) <= max_words:
            return clean
        return " ".join(words[:max_words]) + "..."

    @staticmethod
    def enrich_citation(
        doc_name: str,
        source_type: str = "pdf",
        page_number: int | None = 1,
        heading: str | None = None,
        workspace_name: str | None = None,
        folder_name: str | None = None,
        document_id: Any | None = None,
        chunk_id: str | None = None,
        chunk_index: int | None = 0,
        score: float = 0.95,
        excerpt: str | None = None,
        url: str | None = None,
        line_start: int | None = None,
        line_end: int | None = None,
    ) -> CitationSchema:
        """Creates a fully enriched CitationSchema object."""
        confidence_val, level = CitationService.calculate_confidence(score)
        clean_excerpt = excerpt or "Đoạn văn bản trích xuất từ chỉ mục RAG..."

        return CitationSchema(
            document_id=str(document_id) if document_id else None,
            document_name=doc_name or "Tài liệu",
            workspace_name=workspace_name or "General",
            folder_name=folder_name or "Root",
            page_number=page_number or 1,
            heading=heading or f"Mục {page_number or 1}",
            chunk_id=chunk_id or f"chunk-{chunk_index or 0}",
            chunk_index=chunk_index or 0,
            confidence=confidence_val,
            confidence_level=level,
            source_type=source_type or "pdf",
            excerpt=CitationService.extract_excerpt(clean_excerpt),
            url=url,
            line_start=line_start or 1,
            line_end=line_end or 10,
        )

    @staticmethod
    def format_breadcrumb(citation: CitationSchema) -> List[str]:
        """Generates Workspace > Folder > Document > Heading > Page > Chunk hierarchy."""
        crumbs = []
        if citation.workspace_name:
            crumbs.append(citation.workspace_name)
        if citation.folder_name:
            crumbs.append(citation.folder_name)
        crumbs.append(citation.document_name)
        if citation.heading:
            crumbs.append(citation.heading)
        if citation.page_number:
            crumbs.append(f"Trang {citation.page_number}")
        if citation.chunk_index is not None:
            crumbs.append(f"Chunk #{citation.chunk_index}")
        return crumbs
