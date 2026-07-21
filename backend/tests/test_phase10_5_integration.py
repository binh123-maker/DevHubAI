import uuid
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentBinary, DocumentVersion, DocumentChunk, ProcessingJob
from app.models.user import User, UserRole
from app.models.workspace import Workspace
from app.services.processing_service import execute_processing_job


def test_full_pipeline_with_validation_repair(db_session: Session):
    """Full pipeline: Chunk Builder → Scoring → Validation → Repair → Re-validation → Persistence"""
    user = User(
        email=f"valrep_{uuid.uuid4().hex[:8]}@example.com",
        password_hash="password",
        role=UserRole.USER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    workspace = Workspace(name="ValRep WS", user_id=user.id)
    db_session.add(workspace)
    db_session.commit()
    db_session.refresh(workspace)

    # Markdown with intentional structural issues (unclosed code fence + broken sentence)
    md_path = Path("valrep_doc.md")
    md_path.write_text(
        "# Chapter 1\n```python\ndef hello():\n  pass\nThis sentence has no period\n\n"
        "# Chapter 2\n| Col1 | Col2 |\n|---|\n| Row1 |",
        encoding="utf-8"
    )

    try:
        doc = Document(
            user_id=user.id,
            workspace_id=workspace.id,
            title="ValRep Doc",
            file_name=md_path.name,
            file_type="md",
            file_size=md_path.stat().st_size,
            file_path=str(md_path.absolute()),
            status="uploading"
        )
        db_session.add(doc)
        db_session.commit()
        db_session.refresh(doc)

        binary = DocumentBinary(
            sha256=f"hash_{uuid.uuid4().hex}",
            file_path=str(md_path.absolute()),
            file_type="md",
            file_size=md_path.stat().st_size
        )
        db_session.add(binary)
        db_session.commit()
        db_session.refresh(binary)

        version = DocumentVersion(
            document_id=doc.id,
            version_number=1,
            binary_id=binary.sha256,
            status="uploading"
        )
        db_session.add(version)
        db_session.commit()
        db_session.refresh(version)

        job = ProcessingJob(
            document_version_id=version.id,
            job_type="upload_processing",
            status="pending",
            progress=0,
            retry_count=0
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        execute_processing_job(db_session, job.id)

        db_session.refresh(job)
        assert job.status == "completed"

        chunks = db_session.scalars(
            select(DocumentChunk)
            .where(DocumentChunk.document_version_id == version.id)
            .order_by(DocumentChunk.chunk_index)
        ).all()
        assert len(chunks) > 0

        # Every chunk must carry validation metadata
        meta = chunks[0].metadata_json
        assert "validation_status" in meta
        assert "validation_health" in meta
        assert "validation_score" in meta
        assert "validation_version" in meta
        assert "repair_performed" in meta
        assert "repair_success" in meta
        assert "overall_health" in meta
        assert "pipeline_status" in meta
        assert "rescored" in meta

    finally:
        if md_path.exists():
            md_path.unlink()


def test_valid_chunk_skips_repair(db_session: Session):
    """Clean document: validation passes → repair skipped."""
    user = User(
        email=f"norepar_{uuid.uuid4().hex[:8]}@example.com",
        password_hash="password",
        role=UserRole.USER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    workspace = Workspace(name="NoRepair WS", user_id=user.id)
    db_session.add(workspace)
    db_session.commit()
    db_session.refresh(workspace)

    md_path = Path("clean_doc.md")
    md_path.write_text(
        "# Introduction\nThis is a clean and well-formed document with complete sentences.\n\n"
        "# Conclusion\nEverything is fine and complete.",
        encoding="utf-8"
    )

    try:
        doc = Document(
            user_id=user.id,
            workspace_id=workspace.id,
            title="Clean Doc",
            file_name=md_path.name,
            file_type="md",
            file_size=md_path.stat().st_size,
            file_path=str(md_path.absolute()),
            status="uploading"
        )
        db_session.add(doc)
        db_session.commit()
        db_session.refresh(doc)

        binary = DocumentBinary(
            sha256=f"hash_{uuid.uuid4().hex}",
            file_path=str(md_path.absolute()),
            file_type="md",
            file_size=md_path.stat().st_size
        )
        db_session.add(binary)
        db_session.commit()
        db_session.refresh(binary)

        version = DocumentVersion(
            document_id=doc.id,
            version_number=1,
            binary_id=binary.sha256,
            status="uploading"
        )
        db_session.add(version)
        db_session.commit()
        db_session.refresh(version)

        job = ProcessingJob(
            document_version_id=version.id,
            job_type="upload_processing",
            status="pending",
            progress=0,
            retry_count=0
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        execute_processing_job(db_session, job.id)

        db_session.refresh(job)
        assert job.status == "completed"

        chunks = db_session.scalars(
            select(DocumentChunk)
            .where(DocumentChunk.document_version_id == version.id)
            .order_by(DocumentChunk.chunk_index)
        ).all()
        assert len(chunks) > 0

        meta = chunks[0].metadata_json
        assert "validation_status" in meta
        # Scoring metadata preserved
        assert "overall_score" in meta

    finally:
        if md_path.exists():
            md_path.unlink()
