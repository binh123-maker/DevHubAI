import uuid
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentBinary, DocumentVersion, DocumentStructureNode, DocumentChunk
from app.models.user import User, UserRole
from app.models.workspace import Workspace
from app.services.processors.base import ExtractedDocument, ExtractedPage
from app.services.structure_parser import parse_structure
from app.services.processing_service import _store_chunks
from app.services.chunker import TextChunk

def test_phase3_structure_parsing_and_mapping(db_session: Session):
    # 1. Setup User, Workspace, Document, Binary, Version
    user = User(
        email=f"structtest_{uuid.uuid4().hex[:8]}@example.com",
        password_hash="password",
        role=UserRole.USER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    workspace = Workspace(name="Struct Test Workspace", user_id=user.id)
    db_session.add(workspace)
    db_session.commit()
    db_session.refresh(workspace)

    document = Document(
        user_id=user.id,
        workspace_id=workspace.id,
        title="Struct Doc",
        file_name="struct.md",
        file_type="md",
        file_size=200,
        file_path="/path/to/struct.md",
        status="uploading"
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    binary = DocumentBinary(
        sha256=f"hash_{uuid.uuid4().hex}",
        file_path="/path/to/struct.md",
        file_type="md",
        file_size=200
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

    # 2. Build mock ExtractedDocument with structure
    markdown_content = (
        "# Introduction\n\n"
        "This is the first paragraph introducing the topic.\n\n"
        "## Details\n\n"
        "Here are details.\n\n"
        "```python\ndef test():\n    pass\n```"
    )
    page = ExtractedPage(
        page_number=1,
        raw_text=markdown_content.replace("#", "").replace("```python", "").replace("```", ""),
        markdown=markdown_content
    )
    extracted = ExtractedDocument(pages=[page])

    # 3. Parse structure nodes
    nodes = parse_structure(version.id, extracted)
    assert len(nodes) == 5
    
    # Save nodes
    db_session.add_all(nodes)
    db_session.commit()

    # Verify heading hierarchy
    h1_node = next(n for n in nodes if n.node_type == "heading" and n.hierarchy_level == 1)
    h2_node = next(n for n in nodes if n.node_type == "heading" and n.hierarchy_level == 2)
    p_node1 = next(n for n in nodes if n.node_type == "paragraph" and "first paragraph" in n.content_text)
    code_node = next(n for n in nodes if n.node_type == "code_block")

    assert h1_node.parent_id is None
    assert h2_node.parent_id == h1_node.id
    assert p_node1.parent_id == h1_node.id
    assert code_node.parent_id == h2_node.id
    assert code_node.language == "python"

    # 4. Store Chunks linked to structure nodes
    mock_chunks = [
        {
            "structure_node_id": p_node1.id,
            "chunk_index": 0,
            "content": "This is the first paragraph introducing the topic.",
            "content_markdown": "This is the first paragraph introducing the topic.",
            "page_number": 1,
            "line_start": 1,
            "line_end": 2,
            "char_start": 15,
            "char_end": 65,
            "token_count": 12,
            "char_count": 50,
            "word_count": 8,
            "hash": "hash1",
            "heading": "Introduction"
        },
        {
            "structure_node_id": code_node.id,
            "chunk_index": 1,
            "content": "def test():\n    pass",
            "content_markdown": "```python\ndef test():\n    pass\n```",
            "page_number": 1,
            "line_start": 3,
            "line_end": 5,
            "char_start": 90,
            "char_end": 115,
            "token_count": 6,
            "char_count": 25,
            "word_count": 3,
            "hash": "hash2",
            "heading": "Details"
        }
    ]

    _store_chunks(db_session, document.id, version.id, mock_chunks)

    # Verify chunks mapped
    db_chunks = db_session.query(DocumentChunk).filter(DocumentChunk.document_version_id == version.id).order_by(DocumentChunk.chunk_index).all()
    assert len(db_chunks) == 2
    assert db_chunks[0].structure_node_id == p_node1.id
    assert db_chunks[1].structure_node_id == code_node.id
    assert db_chunks[0].token_count is not None
    assert db_chunks[0].hash is not None

    # Clean up
    for c in db_chunks:
        db_session.delete(c)
    for n in nodes:
        db_session.delete(n)
    db_session.delete(version)
    db_session.delete(binary)
    db_session.delete(document)
    db_session.delete(workspace)
    db_session.delete(user)
    db_session.commit()
