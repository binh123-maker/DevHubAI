"""Base processor interface shared by all format-specific processors."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ExtractedPage:
    """A single page (or synthetic page) of extracted content."""
    page_number: int          # 1-based page index; 0 for formats with no page concept
    raw_text: str             # Plain text
    markdown: str             # Markdown representation


@dataclass
class ExtractedDocument:
    """Full extraction result from a document."""
    pages: list[ExtractedPage] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        return "\n\n".join(p.raw_text for p in self.pages)
