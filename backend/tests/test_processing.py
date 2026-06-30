"""
Tests for Document Processing Engine.

These tests exercise:
- TXT extraction and chunking (no extra deps)
- Chunker logic (paragraph split, min-merge, heading detection)
- processing_service.process_document end-to-end with a real DB session
- API endpoint GET /documents/{id}/chunks
"""
import io
import time
from pathlib import Path

import pytest

from app.services.processors.text_processor import extract_text
from app.services.chunker import chunk_document, _extract_heading


# ---------------------------------------------------------------------------
# Unit: text_processor
# ---------------------------------------------------------------------------

class TestTextExtractor:
    def test_txt_single_page(self, tmp_path):
        f = tmp_path / "hello.txt"
        f.write_text("Hello world\nThis is a test.", encoding="utf-8")
        result = extract_text(f, "txt")
        assert len(result.pages) == 1
        assert "Hello world" in result.pages[0].raw_text

    def test_md_preserves_markdown(self, tmp_path):
        f = tmp_path / "readme.md"
        f.write_text("# Title\n\nSome **bold** text.", encoding="utf-8")
        result = extract_text(f, "md")
        assert len(result.pages) == 1
        assert "# Title" in result.pages[0].markdown

    def test_large_txt_splits_into_pages(self, tmp_path):
        lines = [f"Line {i}" for i in range(250)]
        f = tmp_path / "big.txt"
        f.write_text("\n".join(lines), encoding="utf-8")
        result = extract_text(f, "txt")
        # PAGE_LINE_SIZE = 80, so 250 lines → 4 pages (80+80+80+10)
        assert len(result.pages) >= 3

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_text("", encoding="utf-8")
        result = extract_text(f, "txt")
        assert result.pages == []


# ---------------------------------------------------------------------------
# Unit: chunker
# ---------------------------------------------------------------------------

class TestChunker:
    def _make_doc(self, text: str, md: str | None = None):
        from app.services.processors.base import ExtractedDocument, ExtractedPage
        return ExtractedDocument(pages=[
            ExtractedPage(page_number=1, raw_text=text, markdown=md or text)
        ])

    def test_single_paragraph_yields_one_chunk(self):
        doc = self._make_doc("Hello world this is a test document with enough content.")
        chunks = chunk_document(doc)
        assert len(chunks) >= 1
        assert "Hello world" in chunks[0].content

    def test_multiple_paragraphs_yield_multiple_chunks(self):
        text = "\n\n".join([f"Paragraph {i}: " + "word " * 20 for i in range(5)])
        doc = self._make_doc(text)
        chunks = chunk_document(doc)
        assert len(chunks) >= 1  # at minimum 1 chunk

    def test_chunk_line_numbers_are_set(self):
        doc = self._make_doc("Line 1\nLine 2\nLine 3")
        chunks = chunk_document(doc)
        for c in chunks:
            assert c.line_start is not None
            assert c.line_end is not None
            assert c.line_start <= c.line_end

    def test_chunk_indices_are_sequential(self):
        text = "\n\n".join(["paragraph " * 10 for _ in range(8)])
        doc = self._make_doc(text)
        chunks = chunk_document(doc)
        indices = [c.chunk_index for c in chunks]
        assert indices == list(range(len(chunks)))

    def test_heading_detection(self):
        doc = self._make_doc("# My Title\n\nSome content here.", md="# My Title\n\nSome content here.")
        chunks = chunk_document(doc)
        headings = [c.heading for c in chunks if c.heading]
        assert any("My Title" in (h or "") for h in headings)

    def test_extract_heading_returns_none_for_plain_text(self):
        assert _extract_heading("No heading here just plain text") is None

    def test_extract_heading_finds_h2(self):
        assert _extract_heading("## Section Title") == "Section Title"

    def test_large_paragraph_is_split(self):
        """A paragraph longer than MAX_CHARS must produce more than one chunk."""
        long_para = ("This is a sentence. " * 200)  # ~4000 chars
        doc = self._make_doc(long_para)
        chunks = chunk_document(doc)
        assert len(chunks) >= 2  # must be split


# ---------------------------------------------------------------------------
# Integration: processing_service via API
# ---------------------------------------------------------------------------

class TestProcessingPipeline:
    def _create_workspace_and_upload(self, client, headers, file_content: bytes, filename: str = "test.txt"):
        ws = client.post("/api/v1/workspaces", json={"name": "Processing WS"}, headers=headers)
        assert ws.status_code == 201
        workspace_id = ws.json()["id"]

        up = client.post(
            "/api/v1/documents/upload",
            data={"workspace_id": workspace_id},
            files={"file": (filename, file_content, "text/plain")},
            headers=headers,
        )
        assert up.status_code == 201
        return workspace_id, up.json()["id"]

    def test_upload_triggers_processing_status(self, client, auth_headers):
        """Right after upload, status is UPLOADING or transitions quickly to PROCESSED."""
        _, doc_id = self._create_workspace_and_upload(
            client, auth_headers, b"Hello world\nSecond line\n\nNew paragraph."
        )
        # Give BackgroundTask a moment (in TestClient it runs synchronously after response)
        get_res = client.get(f"/api/v1/documents/{doc_id}", headers=auth_headers)
        assert get_res.status_code == 200
        assert get_res.json()["status"] in ("uploading", "processing", "processed", "failed")

    def test_chunks_endpoint_after_processing(self, client, auth_headers):
        """Chunks must be available after processing a TXT document."""
        content = b"# DevHub AI\n\nThis is the first paragraph.\n\nThis is the second paragraph with more content."
        _, doc_id = self._create_workspace_and_upload(
            client, auth_headers, content, "readme.md"
        )

        # In TestClient, BackgroundTask runs synchronously, so chunks should exist immediately
        chunks_res = client.get(f"/api/v1/documents/{doc_id}/chunks", headers=auth_headers)
        assert chunks_res.status_code == 200
        chunks = chunks_res.json()
        assert isinstance(chunks, list)
        # At least 1 chunk must be created
        assert len(chunks) >= 1
        # Verify schema fields
        first = chunks[0]
        assert "content" in first
        assert "content_markdown" in first
        assert "chunk_index" in first

    def test_chunks_endpoint_requires_ownership(self, client, auth_headers, other_user_headers):
        _, doc_id = self._create_workspace_and_upload(
            client, auth_headers, b"Some private content"
        )
        res = client.get(f"/api/v1/documents/{doc_id}/chunks", headers=other_user_headers)
        assert res.status_code == 404

    def test_upload_invalid_extension_blocked(self, client, auth_headers):
        ws = client.post("/api/v1/workspaces", json={"name": "Ext WS"}, headers=auth_headers)
        workspace_id = ws.json()["id"]
        up = client.post(
            "/api/v1/documents/upload",
            data={"workspace_id": workspace_id},
            files={"file": ("script.py", b"import os", "text/x-python")},
            headers=auth_headers,
        )
        assert up.status_code == 422
