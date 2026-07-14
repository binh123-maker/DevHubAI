import uuid
import pytest
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentBinary, DocumentVersion, ProcessingJob
from app.models.user import User, UserRole
from app.models.workspace import Workspace
from app.services.processing_service import execute_processing_job

def test_phase2_job_retry_on_failure(db_session: Session):
    # 1. Setup User, Workspace, Document
    user = User(
        email=f"jobtest_{uuid.uuid4().hex[:8]}@example.com",
        password_hash="password",
        role=UserRole.USER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    workspace = Workspace(name="Job Test Workspace", user_id=user.id)
    db_session.add(workspace)
    db_session.commit()
    db_session.refresh(workspace)

    document = Document(
        user_id=user.id,
        workspace_id=workspace.id,
        title="Fail Doc",
        file_name="fail.txt",
        file_type="txt",
        file_size=100,
        file_path="/invalid/path/fail.txt",
        status="uploading"
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    binary = DocumentBinary(
        sha256=f"hash_{uuid.uuid4().hex}",
        file_path="/invalid/path/fail.txt",  # triggers FileNotFoundError
        file_type="txt",
        file_size=100
    )
    db_session.add(binary)
    db_session.commit()
    db_session.refresh(binary)

    version = DocumentVersion(
        document_id=document.id,
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
        priority=1,
        retry_count=0,
        progress=0
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    # 2. Execute job - should fail and increment retry_count because file does not exist
    execute_processing_job(db_session, job.id)
    db_session.refresh(job)

    assert job.status == "pending"
    assert job.retry_count == 1
    assert "Retry 1 failed" in job.error_message

    # Clean up
    db_session.delete(job)
    db_session.delete(version)
    db_session.delete(binary)
    db_session.delete(document)
    db_session.delete(workspace)
    db_session.delete(user)
    db_session.commit()


def test_phase2_job_cancellation(db_session: Session):
    # 1. Setup User, Workspace, Document
    user = User(
        email=f"jobtest_{uuid.uuid4().hex[:8]}@example.com",
        password_hash="password",
        role=UserRole.USER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    workspace = Workspace(name="Job Cancel Workspace", user_id=user.id)
    db_session.add(workspace)
    db_session.commit()
    db_session.refresh(workspace)

    document = Document(
        user_id=user.id,
        workspace_id=workspace.id,
        title="Cancel Doc",
        file_name="cancel.txt",
        file_type="txt",
        file_size=100,
        file_path="/invalid/path/cancel.txt",
        status="uploading"
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    binary = DocumentBinary(
        sha256=f"hash_{uuid.uuid4().hex}",
        file_path="/invalid/path/cancel.txt",
        file_type="txt",
        file_size=100
    )
    db_session.add(binary)
    db_session.commit()
    db_session.refresh(binary)

    version = DocumentVersion(
        document_id=document.id,
        version_number=1,
        binary_id=binary.sha256,
        status="uploading"
    )
    db_session.add(version)
    db_session.commit()
    db_session.refresh(version)

    # Pre-cancel the job
    job = ProcessingJob(
        document_version_id=version.id,
        job_type="upload_processing",
        status="cancelled",
        priority=1,
        retry_count=0,
        progress=0
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    # 2. Execute job
    execute_processing_job(db_session, job.id)
    db_session.refresh(job)

    # Status must remain cancelled and not change to pending/running
    assert job.status == "cancelled"

    # Clean up
    db_session.delete(job)
    db_session.delete(version)
    db_session.delete(binary)
    db_session.delete(document)
    db_session.delete(workspace)
    db_session.delete(user)
    db_session.commit()
