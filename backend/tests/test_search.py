import pytest
from uuid import uuid4

def test_search_documents(client, auth_headers):
    # 1. Create workspace
    ws_res = client.post("/api/v1/workspaces", json={"name": "Search WS"}, headers=auth_headers)
    assert ws_res.status_code == 201
    workspace_id = ws_res.json()["id"]

    # 2. Upload document 1
    content1 = b"PostgreSQL is a powerful, open source object-relational database system."
    client.post(
        "/api/v1/documents/upload",
        data={"workspace_id": workspace_id, "title": "Doc 1"},
        files={"file": ("doc1.txt", content1, "text/plain")},
        headers=auth_headers,
    )

    # 3. Upload document 2
    content2 = b"FastAPI is a modern, fast (high-performance), web framework for building APIs with Python."
    client.post(
        "/api/v1/documents/upload",
        data={"workspace_id": workspace_id, "title": "Doc 2"},
        files={"file": ("doc2.txt", content2, "text/plain")},
        headers=auth_headers,
    )

    # Note: In TestClient, BackgroundTasks are executed synchronously,
    # so by the time upload returns, processing is done, chunks are in DB,
    # and the trigger has updated search_vector.

    # 4. Global Search for "database"
    search_res = client.get("/api/v1/search?query=database", headers=auth_headers)
    assert search_res.status_code == 200
    results = search_res.json()
    assert len(results) == 1
    assert "PostgreSQL" in results[0]["content"]

    # 5. Global Search for "python framework"
    search_res2 = client.get("/api/v1/search?query=python framework", headers=auth_headers)
    assert search_res2.status_code == 200
    results2 = search_res2.json()
    assert len(results2) == 1
    assert "FastAPI" in results2[0]["content"]
    assert results2[0]["relevance_score"] > 0

    # 6. Workspace scoped search
    search_res3 = client.get(f"/api/v1/search?query=fastapi&workspace_id={workspace_id}", headers=auth_headers)
    assert search_res3.status_code == 200
    assert len(search_res3.json()) == 1

    # Empty search query should return 422 because of min_length=1
    search_empty = client.get("/api/v1/search?query=", headers=auth_headers)
    assert search_empty.status_code == 422


def test_search_security_isolation(client, auth_headers, other_user_headers):
    # User A creates a document
    ws_res = client.post("/api/v1/workspaces", json={"name": "Secret WS"}, headers=auth_headers)
    workspace_id = ws_res.json()["id"]

    client.post(
        "/api/v1/documents/upload",
        data={"workspace_id": workspace_id, "title": "Secret Doc"},
        files={"file": ("secret.txt", b"This is a top secret document containing passwords.", "text/plain")},
        headers=auth_headers,
    )

    # User B searches for "secret"
    search_b = client.get("/api/v1/search?query=secret", headers=other_user_headers)
    assert search_b.status_code == 200
    assert len(search_b.json()) == 0  # Should not find User A's document

    # User A searches for "secret"
    search_a = client.get("/api/v1/search?query=secret", headers=auth_headers)
    assert search_a.status_code == 200
    assert len(search_a.json()) == 1
