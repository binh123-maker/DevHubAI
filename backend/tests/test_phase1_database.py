import uuid
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentBinary, DocumentVersion, DocumentStructureNode, ProcessingJob, UrlResource

def test_phase1_database_models(db_session: Session):
    # 1. Create a dummy document (needs a workspace and a user, or we can just mock the FK fields since db is a Session)
    # Wait, we can fetch an existing user/workspace from db or create them.
    # Let's create a User and Workspace first to have real valid foreign keys.
    from app.models.user import User, UserRole
    from app.models.workspace import Workspace

    user = User(
        email=f"dbtest_{uuid.uuid4().hex[:8]}@example.com",
        password_hash="password",
        role=UserRole.USER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    workspace = Workspace(
        name="Test DB Workspace",
        user_id=user.id
    )
    db_session.add(workspace)
    db_session.commit()
    db_session.refresh(workspace)

    document = Document(
        user_id=user.id,
        workspace_id=workspace.id,
        title="Logical Doc",
        file_name="logical.txt",
        file_type="txt",
        file_size=100,
        file_path="/path/to/logical.txt",
        status="uploading"
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    # 2. Create UrlResource
    url_res = UrlResource(
        original_url="https://example.com/doc",
        title="Example Webpage",
        description="A simple webpage resource description"
    )
    db_session.add(url_res)
    db_session.commit()
    db_session.refresh(url_res)

    # 3. Create DocumentBinary
    binary = DocumentBinary(
        sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        file_path="/uploads/e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.txt",
        file_type="txt",
        file_size=0
    )
    db_session.add(binary)
    db_session.commit()
    db_session.refresh(binary)

    # 4. Create DocumentVersion
    version = DocumentVersion(
        document_id=document.id,
        version_number=1,
        binary_id=binary.sha256,
        url_resource_id=url_res.id,
        status="processed",
        status_message="Success"
    )
    db_session.add(version)
    db_session.commit()
    db_session.refresh(version)

    # 5. Create DocumentStructureNode
    node = DocumentStructureNode(
        document_version_id=version.id,
        node_category="code",
        node_type="function",
        order_index=0,
        hierarchy_level=1,
        content_text="def test(): pass",
        content_markdown="```python\ndef test(): pass\n```"
    )
    db_session.add(node)
    db_session.commit()
    db_session.refresh(node)

    # 6. Create ProcessingJob
    job = ProcessingJob(
        document_version_id=version.id,
        job_type="upload_processing",
        status="completed",
        priority=1,
        retry_count=0,
        progress=100
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    # Assert relations
    assert len(document.versions) == 1
    assert document.versions[0].id == version.id
    assert version.binary.sha256 == binary.sha256
    assert version.url_resource.id == url_res.id
    assert len(version.structure_nodes) == 1
    assert version.structure_nodes[0].id == node.id
    assert len(version.processing_jobs) == 1
    assert version.processing_jobs[0].id == job.id

    # Clean up
    db_session.delete(job)
    db_session.delete(node)
    db_session.delete(version)
    db_session.delete(binary)
    db_session.delete(url_res)
    db_session.delete(document)
    db_session.delete(workspace)
    db_session.delete(user)
    db_session.commit()
