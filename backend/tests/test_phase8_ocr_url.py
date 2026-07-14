import uuid
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentBinary, DocumentVersion, UrlResource
from app.models.user import User, UserRole
from app.models.workspace import Workspace
from app.services.ocr_pipeline import perform_ocr

def test_phase8_ocr_fallback():
    # Verify ocr fallback returns some extracted page structure
    temp_file = Path("test_ocr_temp.txt")
    with open(temp_file, "w") as f:
        f.write("Scanned page mock content")
    try:
        extracted = perform_ocr(temp_file)
        assert len(extracted.pages) > 0
        assert "mock" in extracted.pages[0].raw_text.lower() or "fallback" in extracted.pages[0].raw_text.lower()
    finally:
        temp_file.unlink(missing_ok=True)


def test_phase8_url_resource_api(client: TestClient, db_session: Session):
    # 1. Create user and authentication headers
    email = f"urlapi_{uuid.uuid4().hex[:8]}@example.com"
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

    response_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "password"}
    )
    token = response_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Setup Workspace, Document, Binary, UrlResource and Version
    workspace = Workspace(name="API Url Workspace", user_id=user.id)
    db_session.add(workspace)
    db_session.commit()
    db_session.refresh(workspace)

    document = Document(
        user_id=user.id,
        workspace_id=workspace.id,
        title="Webpage Doc",
        file_name="webpage.md",
        file_type="md",
        file_size=300,
        file_path="/path/to/webpage.md",
        status="processed"
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    binary = DocumentBinary(
        sha256=f"hash_{uuid.uuid4().hex}",
        file_path="/path/to/webpage.md",
        file_type="md",
        file_size=300
    )
    db_session.add(binary)
    db_session.commit()
    db_session.refresh(binary)

    url_res = UrlResource(
        original_url="http://example.com/test",
        fetched_html="<html><body><h1>Test Page</h1></body></html>",
        parsed_markdown="# Test Page",
        title="Test Title",
        description="Test Page Desc"
    )
    db_session.add(url_res)
    db_session.commit()
    db_session.refresh(url_res)

    version = DocumentVersion(
        document_id=document.id,
        version_number=1,
        binary_id=binary.sha256,
        url_resource_id=url_res.id,
        status="processed"
    )
    db_session.add(version)
    db_session.commit()
    db_session.refresh(version)

    # 3. Request URL Resource parsed details via GET API
    response = client.get(f"/api/v1/documents/{document.id}/url-resource", headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["original_url"] == "http://example.com/test"
    assert res_data["title"] == "Test Title"
    assert res_data["parsed_markdown"] == "# Test Page"

    # Clean up
    from app.models.user import RefreshToken
    db_session.query(RefreshToken).filter(RefreshToken.user_id == user.id).delete()
    db_session.delete(version)
    db_session.delete(url_res)
    db_session.delete(binary)
    db_session.delete(document)
    db_session.delete(workspace)
    db_session.delete(user)
    db_session.commit()
