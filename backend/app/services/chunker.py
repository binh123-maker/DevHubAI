"""
Chunker — splits an ExtractedPage into multiple text chunks.

Strategy
--------
* Split the page text by blank-line-separated paragraphs first.
* If a paragraph exceeds MAX_CHARS, hard-split it at sentence boundaries.
* Track line_start / line_end (1-based) relative to the entire document.
* Preserve the page_number from the source page.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from app.services.processors.base import ExtractedDocument, ExtractedPage

MAX_CHARS = 1500        # Maximum characters per chunk
MIN_CHARS = 80          # Minimum characters — merge tiny paragraphs with next one


@dataclass
class TextChunk:
    page_number: int
    chunk_index: int         # global chunk index across the document (0-based)
    line_start: int          # 1-based line number where this chunk starts (document-level)
    line_end: int            # 1-based line number where this chunk ends (document-level)
    content: str             # plain text
    content_markdown: str    # markdown version
    heading: str | None      # nearest heading above this chunk (if any)


def _split_into_sentences(text: str) -> list[str]:
    """Naïve sentence splitter by punctuation (.!?) followed by space/newline."""
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip() for p in parts if p.strip()]


def _extract_heading(markdown: str) -> str | None:
    """Return the first markdown heading found in the text, or None."""
    for line in markdown.splitlines():
        if line.startswith("#"):
            return re.sub(r"^#+\s*", "", line).strip()
    return None


def chunk_page(page: ExtractedPage, global_line_offset: int, global_chunk_offset: int) -> tuple[list[TextChunk], int]:
    """
    Chunk a single page.

    Returns:
        (chunks, new_global_line_offset)
    """
    raw_paragraphs = re.split(r'\n\s*\n', page.raw_text)
    md_paragraphs = re.split(r'\n\s*\n', page.content_markdown if hasattr(page, 'content_markdown') else page.markdown)

    # Pad lists to same length
    while len(md_paragraphs) < len(raw_paragraphs):
        md_paragraphs.append("")
    while len(raw_paragraphs) < len(md_paragraphs):
        raw_paragraphs.append("")

    # Merge tiny paragraphs
    merged_raw: list[str] = []
    merged_md: list[str] = []

    buffer_raw = ""
    buffer_md = ""

    for raw_p, md_p in zip(raw_paragraphs, md_paragraphs):
        raw_p = raw_p.strip()
        md_p = md_p.strip()
        if not raw_p:
            continue
        if buffer_raw and len(buffer_raw) + len(raw_p) < MIN_CHARS:
            buffer_raw += "\n\n" + raw_p
            buffer_md += "\n\n" + md_p
        else:
            if buffer_raw:
                merged_raw.append(buffer_raw)
                merged_md.append(buffer_md)
            buffer_raw = raw_p
            buffer_md = md_p

    if buffer_raw:
        merged_raw.append(buffer_raw)
        merged_md.append(buffer_md)

    # Build chunks
    chunks: list[TextChunk] = []
    current_line = global_line_offset

    for raw_p, md_p in zip(merged_raw, merged_md):
        # Hard-split if paragraph is still too large
        if len(raw_p) <= MAX_CHARS:
            parts_raw = [raw_p]
            parts_md = [md_p]
        else:
            sentences = _split_into_sentences(raw_p)
            parts_raw = []
            parts_md = []
            buf = ""
            for sent in sentences:
                if len(buf) + len(sent) > MAX_CHARS:
                    if buf:
                        parts_raw.append(buf.strip())
                        parts_md.append(buf.strip())  # best effort for split md
                    buf = sent
                else:
                    buf = (buf + " " + sent).strip() if buf else sent
            if buf:
                parts_raw.append(buf.strip())
                parts_md.append(buf.strip())

        for part_raw, part_md in zip(parts_raw, parts_md):
            line_count = part_raw.count("\n") + 1
            line_start = current_line + 1
            line_end = current_line + line_count

            chunks.append(TextChunk(
                page_number=page.page_number,
                chunk_index=global_chunk_offset + len(chunks),
                line_start=line_start,
                line_end=line_end,
                content=part_raw,
                content_markdown=part_md,
                heading=_extract_heading(part_md),
            ))

            current_line = line_end

    return chunks, current_line


def chunk_document(extracted: ExtractedDocument) -> list[TextChunk]:
    """Chunk all pages of a document into a flat list of TextChunks."""
    all_chunks: list[TextChunk] = []
    global_line = 0
    global_chunk = 0

    for page in extracted.pages:
        # Attach markdown to page temporarily for chunker
        page.content_markdown = page.markdown  # type: ignore[attr-defined]

        page_chunks, global_line = chunk_page(page, global_line, global_chunk)
        all_chunks.extend(page_chunks)
        global_chunk += len(page_chunks)

    return all_chunks
