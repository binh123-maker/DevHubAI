import uuid
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models.document import Document, DocumentBinary, DocumentVersion, DocumentStructureNode
from app.models.user import User, UserRole
from app.models.workspace import Workspace
from app.services.document_structure.node_types import NodeType
from app.services.document_structure.document_structure_analyzer import analyze_document_structure

def test_phase9_5_rebuilt_integrity_and_database_persistence(client: TestClient, db_session: Session):
    # 1. Setup mock user and auth
    email = f"phase9_5_{uuid.uuid4().hex[:8]}@example.com"
    from app.core.security import get_password_hash
    user = User(
        email=email,
        password_hash=get_password_hash("password"),
        role=UserRole.USER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 2. Setup Workspace and Document
    workspace = Workspace(name="API Phase 9_5 Workspace", user_id=user.id)
    db_session.add(workspace)
    db_session.commit()
    db_session.refresh(workspace)

    # 3. Create document version and binary files
    content = (
        "# Main Heading\n"
        "Some paragraph body here.\n"
        "## Sub Heading\n"
        "- List element 1\n"
        "```python\n"
        "print('hello')\n"
        "```\n"
        "| col 1 | col 2 |\n"
        "|---|---|\n"
        "| val 1 | val 2 |\n"
    )
    temp_file = Path("test_phase9_5.md")
    temp_file.write_text(content, encoding="utf-8")

    try:
        document = Document(
            user_id=user.id,
            workspace_id=workspace.id,
            title="Phase 9_5 Doc",
            file_name="test_phase9_5.md",
            file_type="md",
            file_size=len(content),
            file_path=str(temp_file.absolute()),
            status="processed"
        )
        db_session.add(document)
        db_session.commit()
        db_session.refresh(document)

        binary = DocumentBinary(
            sha256=f"hash_{uuid.uuid4().hex}",
            file_path=str(temp_file.absolute()),
            file_type="md",
            file_size=len(content)
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

        # 4. Run the structure parser & metadata repair on this version
        node_dicts = analyze_document_structure(version.id, temp_file, "md")
        
        db_nodes = []
        for d in node_dicts:
            db_nodes.append(
                DocumentStructureNode(
                    id=d["id"],
                    document_version_id=d["document_version_id"],
                    node_category=d["node_category"],
                    node_type=d["node_type"],
                    parent_id=d["parent_id"],
                    order_index=d["order_index"],
                    hierarchy_level=d["hierarchy_level"],
                    page_start=d["page_start"],
                    page_end=d["page_end"],
                    char_start=d["char_start"],
                    char_end=d["char_end"],
                    line_start=d["line_start"],
                    line_end=d["line_end"],
                    language=d["language"],
                    content_text=d["content_text"],
                    content_markdown=d["content_markdown"],
                    metadata_json=d["metadata_json"]
                )
            )
        db_session.add_all(db_nodes)
        db_session.commit()

        # 5. Fetch nodes back from DB to verify persistence and metadata keys
        saved_nodes = db_session.scalars(
            select(DocumentStructureNode)
            .where(DocumentStructureNode.document_version_id == version.id)
            .order_by(DocumentStructureNode.order_index.asc())
        ).all()

        assert len(saved_nodes) > 0
        h1 = saved_nodes[0]
        assert h1.node_type == NodeType.HEADING_1.value
        
        # Verify metadata keys presence
        h1_meta = h1.metadata_json
        assert "word_count" in h1_meta
        assert "token_estimate" in h1_meta
        assert "heading_path" in h1_meta
        assert "section_path" in h1_meta
        assert "contains_code" in h1_meta
        assert "contains_table" in h1_meta
        assert "contains_list" in h1_meta
        assert "reading_time" in h1_meta
        assert "keywords" in h1_meta

        # Verify heading path is correct
        para = saved_nodes[1]
        assert para.metadata_json["heading_path"] == ["Main Heading"]
        assert para.metadata_json["section_path"] == ["Main Heading"]

        sub_head = saved_nodes[2]
        assert sub_head.node_type == NodeType.HEADING_2.value
        assert sub_head.metadata_json["heading_path"] == ["Main Heading"]
        # section_path should include the heading itself
        assert sub_head.metadata_json["section_path"] == ["Main Heading", "Sub Heading"]

        # Clean up database records
        from app.models.user import RefreshToken
        db_session.query(RefreshToken).filter(RefreshToken.user_id == user.id).delete()
        for node in db_nodes:
            db_session.delete(node)
        db_session.delete(version)
        db_session.delete(binary)
        db_session.delete(document)
        db_session.delete(workspace)
        db_session.delete(user)
        db_session.commit()

    finally:
        temp_file.unlink(missing_ok=True)
