import uuid
import time
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.orm import Session
from unittest.mock import patch

from app.models.document import Document, DocumentBinary, DocumentVersion, DocumentChunk, ProcessingJob
from app.models.user import User, UserRole
from app.models.workspace import Workspace
from app.services.processing_service import execute_processing_job
from app.services.scoring.score_cache import ScoreCache

def test_scoring_integration_pipeline_and_metadata(db_session: Session):
    # 1. Setup User and Workspace
    user = User(
        email=f"score_integ_{uuid.uuid4().hex[:8]}@example.com",
        password_hash="password",
        role=UserRole.USER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    workspace = Workspace(name="Scoring WS", user_id=user.id)
    db_session.add(workspace)
    db_session.commit()
    db_session.refresh(workspace)

    # 2. Markdown File
    md_path = Path("score_doc.md")
    md_path.write_text("# Chapter 1\nSome initial paragraph content text.\n\n# Chapter 2\nMore detailed text.", encoding="utf-8")

    try:
        doc = Document(
            user_id=user.id,
            workspace_id=workspace.id,
            title="Score Doc",
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

        # Trigger execution
        execute_processing_job(db_session, job.id)
        
        # Reload status
        db_session.refresh(job)
        assert job.status == "completed"

        # Verify scoring metadata is stored on the document chunk
        chunks = db_session.scalars(
            select(DocumentChunk)
            .where(DocumentChunk.document_version_id == version.id)
            .order_by(DocumentChunk.chunk_index)
        ).all()
        assert len(chunks) > 0
        
        meta = chunks[0].metadata_json
        assert "overall_score" in meta
        assert "quality_score" in meta
        assert "recommended_retrieval_mode" in meta
        assert "score_signature" in meta
        assert "scoring_version" in meta
        assert "scoring_trace" in meta
        assert "keywords" in meta  # merged intelligently with standard keywords extraction

    finally:
        if md_path.exists():
            md_path.unlink()


def test_scoring_pipeline_failure_recovery(db_session: Session):
    # Setup User and Workspace
    user = User(
        email=f"fail_score_{uuid.uuid4().hex[:8]}@example.com",
        password_hash="password",
        role=UserRole.USER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    workspace = Workspace(name="Scoring Fail WS", user_id=user.id)
    db_session.add(workspace)
    db_session.commit()
    db_session.refresh(workspace)

    md_path = Path("fail_score_doc.md")
    md_path.write_text("# Chapter 1\nSome paragraph text here.", encoding="utf-8")

    try:
        doc = Document(
            user_id=user.id,
            workspace_id=workspace.id,
            title="Fail Score Doc",
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

        # Force exception on ChunkScoringEngine.score_chunks
        with patch("app.services.scoring.chunk_scoring_engine.ChunkScoringEngine.score_chunks", side_effect=Exception("Simulated scoring error")):
            execute_processing_job(db_session, job.id)

        # Pipeline should still succeed
        db_session.refresh(job)
        assert job.status == "completed"

        chunks = db_session.scalars(
            select(DocumentChunk)
            .where(DocumentChunk.document_version_id == version.id)
            .order_by(DocumentChunk.chunk_index)
        ).all()
        assert len(chunks) > 0
        
        # Verify fallback metadata values written
        meta = chunks[0].metadata_json
        assert meta["overall_score"] == 0.5
        assert meta["quality_score"] == 0.5
        assert meta["recommendation"] == "GOOD_FOR_RETRIEVAL"
        assert meta["score_hash"] == ""

    finally:
        if md_path.exists():
            md_path.unlink()
