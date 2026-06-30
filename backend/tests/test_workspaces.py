def test_workspace_crud_flow(client, auth_headers):
    create_response = client.post(
        "/api/v1/workspaces",
        json={
            "name": "ReactJS",
            "description": "React learning materials",
            "color": "#3B82F6",
            "icon": "folder",
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    created = create_response.json()
    workspace_id = created["id"]
    assert created["name"] == "ReactJS"
    assert created["description"] == "React learning materials"
    assert created["color"] == "#3B82F6"

    list_response = client.get("/api/v1/workspaces", headers=auth_headers)
    assert list_response.status_code == 200
    workspaces = list_response.json()
    assert len(workspaces) == 1
    assert workspaces[0]["id"] == workspace_id

    get_response = client.get(f"/api/v1/workspaces/{workspace_id}", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "ReactJS"

    update_response = client.put(
        f"/api/v1/workspaces/{workspace_id}",
        json={"name": "React Advanced", "color": "#10B981"},
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["name"] == "React Advanced"
    assert updated["color"] == "#10B981"
    assert updated["description"] == "React learning materials"

    delete_response = client.delete(f"/api/v1/workspaces/{workspace_id}", headers=auth_headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Workspace deleted successfully"

    missing_response = client.get(f"/api/v1/workspaces/{workspace_id}", headers=auth_headers)
    assert missing_response.status_code == 404


def test_workspace_ownership_isolation(client, auth_headers, other_user_headers):
    create_response = client.post(
        "/api/v1/workspaces",
        json={"name": "Private Workspace"},
        headers=auth_headers,
    )
    workspace_id = create_response.json()["id"]

    get_response = client.get(f"/api/v1/workspaces/{workspace_id}", headers=other_user_headers)
    assert get_response.status_code == 404

    update_response = client.put(
        f"/api/v1/workspaces/{workspace_id}",
        json={"name": "Hacked"},
        headers=other_user_headers,
    )
    assert update_response.status_code == 404

    delete_response = client.delete(f"/api/v1/workspaces/{workspace_id}", headers=other_user_headers)
    assert delete_response.status_code == 404

    owner_get_response = client.get(f"/api/v1/workspaces/{workspace_id}", headers=auth_headers)
    assert owner_get_response.status_code == 200


def test_workspace_requires_authentication(client):
    response = client.get("/api/v1/workspaces")
    assert response.status_code == 401


def test_create_workspace_invalid_color(client, auth_headers):
    response = client.post(
        "/api/v1/workspaces",
        json={"name": "Bad Color", "color": "blue"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_list_workspaces_only_returns_own(client, auth_headers, other_user_headers):
    client.post("/api/v1/workspaces", json={"name": "Owner WS 1"}, headers=auth_headers)
    client.post("/api/v1/workspaces", json={"name": "Owner WS 2"}, headers=auth_headers)
    client.post("/api/v1/workspaces", json={"name": "Other WS"}, headers=other_user_headers)

    owner_list = client.get("/api/v1/workspaces", headers=auth_headers).json()
    other_list = client.get("/api/v1/workspaces", headers=other_user_headers).json()

    assert len(owner_list) == 2
    assert len(other_list) == 1
    assert owner_list[0]["name"] == "Owner WS 2"
