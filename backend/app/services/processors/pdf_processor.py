"""PDF text extraction using PyMuPDF (fitz)."""
from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF

from app.services.processors.base import ExtractedDocument, ExtractedPage


def extract_pdf(file_path: Path) -> ExtractedDocument:
    """
    Extract text from every page of a PDF.

    Strategy:
    - Use fitz.Page.get_text("text") for raw plaintext.
    - Use fitz.Page.get_text("markdown") for markdown (available in PyMuPDF ≥ 1.24).
      Falls back to raw text wrapped in a code block if markdown extraction is unavailable.
    """
    doc = fitz.open(str(file_path))
    pages: list[ExtractedPage] = []

    for page_num, page in enumerate(doc, start=1):
        raw_text: str = page.get_text("text").strip()  # type: ignore[arg-type]

        # PyMuPDF ≥ 1.24 supports "markdown" output
        try:
            md_text: str = page.get_text("markdown").strip()  # type: ignore[arg-type]
        except Exception:
            # Graceful fallback: wrap plain text as preformatted markdown
            md_text = raw_text

        if raw_text:  # skip blank pages
            pages.append(ExtractedPage(
                page_number=page_num,
                raw_text=raw_text,
                markdown=md_text,
            ))

    doc.close()
    return ExtractedDocument(pages=pages)
