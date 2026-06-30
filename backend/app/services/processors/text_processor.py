"""TXT and Markdown text extraction."""
from __future__ import annotations

from pathlib import Path

from app.services.processors.base import ExtractedDocument, ExtractedPage

PAGE_LINE_SIZE = 80  # lines per synthetic page for TXT files


def extract_text(file_path: Path, file_type: str) -> ExtractedDocument:
    """
    Extract text from a .txt or .md file.

    For .md files the source IS the markdown — we store it directly.
    For .txt files we store raw text; markdown equals raw text (no conversion).

    Both are split into synthetic 'pages' of PAGE_LINE_SIZE lines.
    """
    raw_content = file_path.read_text(encoding="utf-8", errors="replace")
    lines = raw_content.splitlines()

    pages: list[ExtractedPage] = []
    is_markdown = file_type.lower() == "md"

    for page_idx, start in enumerate(range(0, max(len(lines), 1), PAGE_LINE_SIZE), start=1):
        chunk_lines = lines[start : start + PAGE_LINE_SIZE]
        raw_text = "\n".join(chunk_lines).strip()

        if not raw_text:
            continue

        # For .md files the raw text IS valid markdown.
        # For .txt files, wrap content as-is (no transformation needed).
        markdown = raw_text if is_markdown else raw_text

        pages.append(ExtractedPage(
            page_number=page_idx,
            raw_text=raw_text,
            markdown=markdown,
        ))

    return ExtractedDocument(pages=pages)
