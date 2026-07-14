import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentBinary, DocumentVersion, DocumentStructureNode
from app.models.user import User, UserRole
from app.models.workspace import Workspace

def test_phase7_document_structure_api(client: TestClient, db_session: Session):
    # 1. Create a user and get auth header
    email = f"structapi_{uuid.uuid4().hex[:8]}@example.com"
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

    # Login to get access token
    response_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "password"}
    )
    token = response_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Setup Workspace and Document
    workspace = Workspace(name="API Struct Workspace", user_id=user.id)
    db_session.add(workspace)
    db_session.commit()
    db_session.refresh(workspace)

    document = Document(
        user_id=user.id,
        workspace_id=workspace.id,
        title="API Struct Doc",
        file_name="apistruct.txt",
        file_type="txt",
        file_size=120,
        file_path="/path/to/apistruct.txt",
        status="processed"
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    binary = DocumentBinary(
        sha256=f"hash_{uuid.uuid4().hex}",
        file_path="/path/to/apistruct.txt",
        file_type="txt",
        file_size=120
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

    # 3. Create structure node
    node = DocumentStructureNode(
        id=uuid.uuid4(),
        document_version_id=version.id,
        node_category="layout",
        node_type="heading",
        order_index=0,
        hierarchy_level=1,
        page_start=1,
        page_end=1,
        char_start=0,
        char_end=10,
        line_start=1,
        line_end=1,
        content_text="# Title",
        content_markdown="# Title"
    )
    db_session.add(node)
    db_session.commit()
    db_session.refresh(node)

    # 4. Fetch structure via GET API
    response = client.get(f"/api/v1/documents/{document.id}/structure", headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert len(res_data) == 1
    assert res_data[0]["node_type"] == "heading"
    assert res_data[0]["content_text"] == "# Title"
    assert res_data[0]["char_start"] == 0

    # Clean up
    from app.models.user import RefreshToken
    db_session.query(RefreshToken).filter(RefreshToken.user_id == user.id).delete()
    db_session.delete(node)
    db_session.delete(version)
    db_session.delete(binary)
    db_session.delete(document)
    db_session.delete(workspace)
    db_session.delete(user)
    db_session.commit()
