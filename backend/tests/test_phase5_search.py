import uuid
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentBinary, DocumentVersion, DocumentStructureNode, DocumentChunk
from app.models.user import User, UserRole
from app.models.workspace import Workspace
from app.services.search_service import search_documents

def test_phase5_advanced_search_ranking(db_session: Session):
    # Setup database records
    user = User(
        email=f"searchtest_{uuid.uuid4().hex[:8]}@example.com",
        password_hash="password",
        role=UserRole.USER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    workspace = Workspace(name="Search Test Workspace", user_id=user.id)
    db_session.add(workspace)
    db_session.commit()
    db_session.refresh(workspace)

    document = Document(
        user_id=user.id,
        workspace_id=workspace.id,
        title="Search Doc",
        file_name="search.txt",
        file_type="txt",
        file_size=150,
        file_path="/path/to/search.txt",
        status="processed"  # Must be processed to be searchable
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    binary = DocumentBinary(
        sha256=f"hash_{uuid.uuid4().hex}",
        file_path="/path/to/search.txt",
        file_type="txt",
        file_size=150
    )
    db_session.add(binary)
    db_session.commit()
    db_session.refresh(binary)

    version = DocumentVersion(
        document_id=document.id,
        version_number=1,
        binary_id=binary.sha256,
        status="processed"
    )
    db_session.add(version)
    db_session.commit()
    db_session.refresh(version)

    # 1. Create a chunk matching code search (FastAPI router metadata)
    chunk1 = DocumentChunk(
        document_id=document.id,
        document_version_id=version.id,
        chunk_index=0,
        content="This is standard text content describing document models.",
        content_markdown="This is standard text content describing document models.",
        page_number=1,
        line_start=1,
        line_end=2,
        char_start=0,
        char_end=50,
        heading="Header",
        metadata_json={
            "routes": ["/api/v1/users"],
            "functions": ["get_user_profile"],
            "frameworks": ["FastAPI"]
        }
    )
    # 2. Create another chunk matching metadata search (simple keywords metadata)
    chunk2 = DocumentChunk(
        document_id=document.id,
        document_version_id=version.id,
        chunk_index=1,
        content="Another chunk with completely different words here.",
        content_markdown="Another chunk with completely different words here.",
        page_number=1,
        line_start=3,
        line_end=4,
        char_start=60,
        char_end=110,
        heading="Header",
        metadata_json={
            "keywords": ["fox", "lazy", "dog"]
        }
    )
    db_session.add_all([chunk1, chunk2])
    db_session.commit()
    db_session.refresh(chunk1)
    db_session.refresh(chunk2)

    # 3. Test Code Search Match (query: "profile")
    results = search_documents(db_session, user.id, "profile", workspace.id)
    assert len(results) > 0
    assert results[0].chunk_id == chunk1.id
    # Score should be at least code search bonus (0.8)
    assert results[0].relevance_score >= 0.8

    # 4. Test Metadata Search Match (query: "lazy")
    results_meta = search_documents(db_session, user.id, "lazy", workspace.id)
    assert len(results_meta) > 0
    assert results_meta[0].chunk_id == chunk2.id
    # Score should be at least metadata search bonus (0.5)
    assert results_meta[0].relevance_score >= 0.5

    # Clean up
    db_session.delete(chunk1)
    db_session.delete(chunk2)
    db_session.delete(version)
    db_session.delete(binary)
    db_session.delete(document)
    db_session.delete(workspace)
    db_session.delete(user)
    db_session.commit()
