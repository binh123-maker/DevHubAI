import uuid
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentBinary, DocumentVersion, DocumentStructureNode, DocumentChunk
from app.models.user import User, UserRole
from app.models.workspace import Workspace
from app.services.metadata_builder import build_metadata
from app.services.chunk_builder import build_chunks_from_structure
from app.services.index_builder import PostgresIndexBuilder

def test_phase4_metadata_builder():
    # Test text metadata extraction
    text_content = "The fast brown fox jumps over the lazy dog. Fox is very fast and lazy."
    text_meta = build_metadata(text_content, is_code=False)
    assert "keywords" in text_meta
    assert len(text_meta["keywords"]) > 0

    # Test code metadata extraction (FastAPI python code)
    code_content = (
        "from fastapi import FastAPI, APIRouter\n"
        "from app.models import Document\n"
        "router = APIRouter()\n"
        "@router.get('/api/v1/docs')\n"
        "def list_docs():\n"
        "    pass\n"
    )
    code_meta = build_metadata(code_content, is_code=True, language="python")
    assert "frameworks" in code_meta
    assert "FastAPI" in code_meta["frameworks"]
    assert "imports" in code_meta
    assert any("fastapi.FastAPI" in imp for imp in code_meta["imports"])
    assert "routes" in code_meta
    assert "/api/v1/docs" in code_meta["routes"]
    assert "functions" in code_meta
    assert "list_docs" in code_meta["functions"]


def test_phase4_chunk_builder_and_index_builder(db_session: Session):
    # Setup database records
    user = User(
        email=f"idxtest_{uuid.uuid4().hex[:8]}@example.com",
        password_hash="password",
        role=UserRole.USER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    workspace = Workspace(name="Index Test Workspace", user_id=user.id)
    db_session.add(workspace)
    db_session.commit()
    db_session.refresh(workspace)

    document = Document(
        user_id=user.id,
        workspace_id=workspace.id,
        title="Index Doc",
        file_name="index.txt",
        file_type="txt",
        file_size=150,
        file_path="/path/to/index.txt",
        status="uploading"
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    binary = DocumentBinary(
        sha256=f"hash_{uuid.uuid4().hex}",
        file_path="/path/to/index.txt",
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
        status="uploading"
    )
    db_session.add(version)
    db_session.commit()
    db_session.refresh(version)

    # 1. Create Structure Nodes
    h1_node = DocumentStructureNode(
        id=uuid.uuid4(),
        document_version_id=version.id,
        node_category="layout",
        node_type="heading",
        order_index=0,
        hierarchy_level=1,
        content_text="# Title",
        content_markdown="# Title"
    )
    p_node = DocumentStructureNode(
        id=uuid.uuid4(),
        document_version_id=version.id,
        node_category="layout",
        node_type="paragraph",
        parent_id=h1_node.id,
        order_index=1,
        hierarchy_level=0,
        content_text="This is indexable text inside a paragraph.",
        content_markdown="This is indexable text inside a paragraph."
    )
    nodes = [h1_node, p_node]
    db_session.add_all(nodes)
    db_session.commit()

    # 2. Build Chunks from Structure
    chunk_dicts = build_chunks_from_structure(nodes)
    assert len(chunk_dicts) == 1
    assert chunk_dicts[0]["structure_node_id"] == p_node.id
    assert chunk_dicts[0]["heading"] == "Title"
    assert chunk_dicts[0]["char_count"] > 0
    assert chunk_dicts[0]["token_count"] > 0

    # Save Chunk
    db_chunk = DocumentChunk(
        document_id=document.id,
        document_version_id=version.id,
        structure_node_id=chunk_dicts[0]["structure_node_id"],
        chunk_index=chunk_dicts[0]["chunk_index"],
        content=chunk_dicts[0]["content"],
        content_markdown=chunk_dicts[0]["content_markdown"],
        page_number=chunk_dicts[0]["page_number"],
        line_start=chunk_dicts[0]["line_start"],
        line_end=chunk_dicts[0]["line_end"],
        char_start=chunk_dicts[0]["char_start"],
        char_end=chunk_dicts[0]["char_end"],
        token_count=chunk_dicts[0]["token_count"],
        char_count=chunk_dicts[0]["char_count"],
        word_count=chunk_dicts[0]["word_count"],
        hash=chunk_dicts[0]["hash"],
        heading=chunk_dicts[0]["heading"],
        metadata_json=build_metadata(chunk_dicts[0]["content"], is_code=False)
    )
    db_session.add(db_chunk)
    db_session.commit()

    # Verify initially search_vector is set (due to DB trigger)
    db_session.refresh(db_chunk)
    assert db_chunk.search_vector is not None

    # 3. Index Builder
    PostgresIndexBuilder().index_version_chunks(db_session, version.id)
    db_session.refresh(db_chunk)
    assert db_chunk.search_vector is not None

    # Clean up
    db_session.delete(db_chunk)
    db_session.delete(p_node)
    db_session.delete(h1_node)
    db_session.delete(version)
    db_session.delete(binary)
    db_session.delete(document)
    db_session.delete(workspace)
    db_session.delete(user)
    db_session.commit()
