import io
from uuid import uuid4

def test_document_upload_and_list(client, auth_headers):
    # 1. Create workspace
    ws_res = client.post("/api/v1/workspaces", json={"name": "Doc WS"}, headers=auth_headers)
    assert ws_res.status_code == 201
    workspace_id = ws_res.json()["id"]

    # 2. Upload document
    file_content = b"Hello world, this is a test document."
    files = {
        "file": ("test.txt", file_content, "text/plain")
    }
    data = {
        "workspace_id": workspace_id,
        "title": "My Test Doc",
        "description": "Test description"
    }

    upload_res = client.post(
        "/api/v1/documents/upload",
        data=data,
        files=files,
        headers=auth_headers,
    )
    assert upload_res.status_code == 201
    doc = upload_res.json()
    doc_id = doc["id"]
    assert doc["title"] == "My Test Doc"
    assert doc["file_name"] == "test.txt"
    assert doc["file_type"] == "txt"
    assert doc["file_size"] == len(file_content)

    # 3. List documents
    list_res = client.get(f"/api/v1/documents?workspace_id={workspace_id}", headers=auth_headers)
    assert list_res.status_code == 200
    docs = list_res.json()
    assert len(docs) == 1
    assert docs[0]["id"] == doc_id

    # 4. Get document
    get_res = client.get(f"/api/v1/documents/{doc_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "My Test Doc"

    # 5. Delete document
    delete_res = client.delete(f"/api/v1/documents/{doc_id}", headers=auth_headers)
    assert delete_res.status_code == 200


def test_document_invalid_extension(client, auth_headers):
    ws_res = client.post("/api/v1/workspaces", json={"name": "Doc WS 2"}, headers=auth_headers)
    workspace_id = ws_res.json()["id"]

    file_content = b"print('hello')"
    files = {
        "file": ("script.py", file_content, "text/x-python")
    }
    data = {"workspace_id": workspace_id}

    upload_res = client.post(
        "/api/v1/documents/upload",
        data=data,
        files=files,
        headers=auth_headers,
    )
    assert upload_res.status_code == 422
    assert "File type not allowed" in upload_res.json()["detail"]


def test_document_ownership_isolation(client, auth_headers, other_user_headers):
    ws_res = client.post("/api/v1/workspaces", json={"name": "User A WS"}, headers=auth_headers)
    workspace_id = ws_res.json()["id"]

    # User B tries to upload to User A's workspace
    files = {"file": ("test.txt", b"content", "text/plain")}
    data = {"workspace_id": workspace_id}
    
    upload_res = client.post(
        "/api/v1/documents/upload",
        data=data,
        files=files,
        headers=other_user_headers,
    )
    assert upload_res.status_code == 404 # Because get_owned_workspace raises 404
