def test_dashboard_overview(client, auth_headers):
    # 1. Create a workspace
    ws_res = client.post(
        "/api/v1/workspaces",
        json={"name": "CS Workspace", "description": "Computer Science"},
        headers=auth_headers,
    )
    assert ws_res.status_code == 201

    # 2. Fetch dashboard overview
    dash_res = client.get("/api/v1/dashboard/overview", headers=auth_headers)
    assert dash_res.status_code == 200
    data = dash_res.json()

    assert "statistics" in data
    assert data["statistics"]["total_workspaces"] >= 1
    assert "total_folders" in data["statistics"]
    assert "total_documents" in data["statistics"]
    assert "total_conversations" in data["statistics"]
    assert "total_messages" in data["statistics"]

    assert "learning_analytics" in data
    assert "heatmap" in data
    assert len(data["heatmap"]) == 90
    assert "recent_activities" in data


def test_document_kanban_status_update(client, auth_headers):
    # 1. Create workspace
    ws_res = client.post(
        "/api/v1/workspaces",
        json={"name": "Kanban Test WS"},
        headers=auth_headers,
    )
    assert ws_res.status_code == 201
    ws_id = ws_res.json()["id"]

    # 2. Upload document
    upload_res = client.post(
        "/api/v1/documents/upload",
        data={"workspace_id": ws_id, "title": "Test Doc for Kanban"},
        files={"file": ("test.txt", b"Kanban Content", "text/plain")},
        headers=auth_headers,
    )
    assert upload_res.status_code == 201
    doc = upload_res.json()
    doc_id = doc["id"]
    assert doc["kanban_status"] == "new"

    # 3. Update kanban status to 'learning'
    update_res = client.patch(
        f"/api/v1/documents/{doc_id}/kanban-status",
        json={"kanban_status": "learning"},
        headers=auth_headers,
    )
    assert update_res.status_code == 200
    updated_doc = update_res.json()
    assert updated_doc["kanban_status"] == "learning"

    # 4. Update kanban status to 'completed'
    update_res2 = client.patch(
        f"/api/v1/documents/{doc_id}/kanban-status",
        json={"kanban_status": "completed"},
        headers=auth_headers,
    )
    assert update_res2.status_code == 200
    assert update_res2.json()["kanban_status"] == "completed"
