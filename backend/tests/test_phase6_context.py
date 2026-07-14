import uuid
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentBinary, DocumentVersion, DocumentStructureNode, DocumentChunk
from app.models.user import User, UserRole
from app.models.workspace import Workspace
from app.schemas.search import SearchResult
from app.services.context_builder import ContextBuilder

def test_phase6_context_builder(db_session: Session):
    # Setup database records
    user = User(
        email=f"ctxtest_{uuid.uuid4().hex[:8]}@example.com",
        password_hash="password",
        role=UserRole.USER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    workspace = Workspace(name="Context Test Workspace", user_id=user.id)
    db_session.add(workspace)
    db_session.commit()
    db_session.refresh(workspace)

    document = Document(
        user_id=user.id,
        workspace_id=workspace.id,
        title="Context Doc",
        file_name="context.txt",
        file_type="txt",
        file_size=150,
        file_path="/path/to/context.txt",
        status="processed"
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    binary = DocumentBinary(
        sha256=f"hash_{uuid.uuid4().hex}",
        file_path="/path/to/context.txt",
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

    # Create structure tree nodes to verify parent trails
    h1 = DocumentStructureNode(
        id=uuid.uuid4(),
        document_version_id=version.id,
        node_category="layout",
        node_type="heading",
        order_index=0,
        hierarchy_level=1,
        content_text="# Overview",
        content_markdown="# Overview"
    )
    h2 = DocumentStructureNode(
        id=uuid.uuid4(),
        document_version_id=version.id,
        node_category="layout",
        node_type="heading",
        parent_id=h1.id,
        order_index=1,
        hierarchy_level=2,
        content_text="## Architecture Details",
        content_markdown="## Architecture Details"
    )
    p_node = DocumentStructureNode(
        id=uuid.uuid4(),
        document_version_id=version.id,
        node_category="layout",
        node_type="paragraph",
        parent_id=h2.id,
        order_index=2,
        hierarchy_level=0,
        content_text="Detail sentence paragraph.",
        content_markdown="Detail sentence paragraph."
    )
    db_session.add_all([h1, h2, p_node])
    db_session.commit()

    # Create adjacent chunks for merging
    chunk1 = DocumentChunk(
        document_id=document.id,
        document_version_id=version.id,
        structure_node_id=p_node.id,
        chunk_index=0,
        content="First paragraph line.",
        content_markdown="First paragraph line.",
        page_number=1,
        line_start=1,
        line_end=2,
        char_start=0,
        char_end=20,
        heading="Overview"
    )
    chunk2 = DocumentChunk(
        document_id=document.id,
        document_version_id=version.id,
        structure_node_id=p_node.id,
        chunk_index=1,
        content="Second paragraph line.",
        content_markdown="Second paragraph line.",
        page_number=1,
        line_start=3,
        line_end=4,
        char_start=21,
        char_end=42,
        heading="Overview"
    )
    db_session.add_all([chunk1, chunk2])
    db_session.commit()
    db_session.refresh(chunk1)
    db_session.refresh(chunk2)

    # Setup search results
    search_results = [
        SearchResult(
            chunk_id=chunk1.id,
            document_id=document.id,
            document_name="context.txt",
            content="First paragraph line.",
            page_number=1,
            line_start=1,
            line_end=2,
            heading="Overview",
            source_url="http://example.com",
            relevance_score=0.9,
            chunk_index=0
        ),
        SearchResult(
            chunk_id=chunk2.id,
            document_id=document.id,
            document_name="context.txt",
            content="Second paragraph line.",
            page_number=1,
            line_start=3,
            line_end=4,
            heading="Overview",
            source_url="http://example.com",
            relevance_score=0.8,
            chunk_index=1
        )
    ]

    # Execute Context Builder
    builder = ContextBuilder(token_budget=100)
    context_str, mappings = builder.build_context(db_session, search_results)

    # Chunks 0 and 1 are adjacent; they must be merged!
    assert "First paragraph line.\nSecond paragraph line." in context_str
    # heading trail must expand to include H1 > H2: "Overview > Architecture Details"
    assert "Overview > Architecture Details" in context_str
    assert len(mappings) == 2

    # Clean up
    db_session.delete(chunk1)
    db_session.delete(chunk2)
    db_session.delete(p_node)
    db_session.delete(h2)
    db_session.delete(h1)
    db_session.delete(version)
    db_session.delete(binary)
    db_session.delete(document)
    db_session.delete(workspace)
    db_session.delete(user)
    db_session.commit()
