def test_folder_crud_flow(client, auth_headers):
    # Create workspace first
    workspace_res = client.post(
        "/api/v1/workspaces",
        json={"name": "Folder Test WS"},
        headers=auth_headers,
    )
    assert workspace_res.status_code == 201
    workspace_id = workspace_res.json()["id"]

    # Create folder
    create_res = client.post(
        "/api/v1/folders",
        json={
            "workspace_id": workspace_id,
            "name": "Documents",
            "description": "Important docs"
        },
        headers=auth_headers,
    )
    assert create_res.status_code == 201
    folder = create_res.json()
    folder_id = folder["id"]
    assert folder["name"] == "Documents"
    assert folder["workspace_id"] == workspace_id
    assert folder["description"] == "Important docs"

    # List folders
    list_res = client.get(f"/api/v1/folders?workspace_id={workspace_id}", headers=auth_headers)
    assert list_res.status_code == 200
    folders = list_res.json()
    assert len(folders) == 1
    assert folders[0]["id"] == folder_id

    # Get folder
    get_res = client.get(f"/api/v1/folders/{folder_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Documents"

    # Update folder
    update_res = client.put(
        f"/api/v1/folders/{folder_id}",
        json={"name": "Archived Docs"},
        headers=auth_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Archived Docs"

    # Delete folder
    delete_res = client.delete(f"/api/v1/folders/{folder_id}", headers=auth_headers)
    assert delete_res.status_code == 200
    
    # Verify deletion
    get_res_after_delete = client.get(f"/api/v1/folders/{folder_id}", headers=auth_headers)
    assert get_res_after_delete.status_code == 404


def test_folder_ownership_isolation(client, auth_headers, other_user_headers):
    # User A creates workspace and folder
    ws_res = client.post(
        "/api/v1/workspaces",
        json={"name": "User A WS"},
        headers=auth_headers,
    )
    workspace_id = ws_res.json()["id"]

    create_res = client.post(
        "/api/v1/folders",
        json={"workspace_id": workspace_id, "name": "Secret Folder"},
        headers=auth_headers,
    )
    folder_id = create_res.json()["id"]

    # User B tries to get folder
    get_res = client.get(f"/api/v1/folders/{folder_id}", headers=other_user_headers)
    assert get_res.status_code == 404

    # User B tries to update folder
    update_res = client.put(
        f"/api/v1/folders/{folder_id}",
        json={"name": "Hacked Folder"},
        headers=other_user_headers,
    )
    assert update_res.status_code == 404

    # User B tries to delete folder
    delete_res = client.delete(f"/api/v1/folders/{folder_id}", headers=other_user_headers)
    assert delete_res.status_code == 404

    # User B tries to list folders in User A's workspace
    list_res = client.get(f"/api/v1/folders?workspace_id={workspace_id}", headers=other_user_headers)
    assert list_res.status_code == 404

    # User B tries to create folder in User A's workspace
    create_hacked_res = client.post(
        "/api/v1/folders",
        json={"workspace_id": workspace_id, "name": "Hacked Folder 2"},
        headers=other_user_headers,
    )
    assert create_hacked_res.status_code == 404


def test_prevent_duplicate_folder_names(client, auth_headers):
    ws_res = client.post(
        "/api/v1/workspaces",
        json={"name": "Unique WS"},
        headers=auth_headers,
    )
    workspace_id = ws_res.json()["id"]

    client.post(
        "/api/v1/folders",
        json={"workspace_id": workspace_id, "name": "Assets"},
        headers=auth_headers,
    )

    duplicate_res = client.post(
        "/api/v1/folders",
        json={"workspace_id": workspace_id, "name": "Assets"},
        headers=auth_headers,
    )
    assert duplicate_res.status_code == 409
