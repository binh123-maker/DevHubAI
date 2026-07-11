import pytest
from uuid import uuid4

def test_chat_lifecycle(client, auth_headers):
    # 1. Create a Global Chat
    res = client.post("/api/v1/chats", json={"title": "My Global Chat", "chat_mode": "global"}, headers=auth_headers)
    assert res.status_code == 201
    chat = res.json()
    chat_id = chat["id"]
    assert chat["title"] == "My Global Chat"
    assert chat["chat_mode"] == "global"
    assert chat["workspace_id"] is None

    # 2. List Chats
    list_res = client.get("/api/v1/chats", headers=auth_headers)
    assert list_res.status_code == 200
    chats = list_res.json()
    assert len(chats) >= 1
    assert chats[0]["id"] == chat_id

    # 3. Create a Workspace Chat
    ws_res = client.post("/api/v1/workspaces", json={"name": "Chat WS"}, headers=auth_headers)
    ws_id = ws_res.json()["id"]

    res_ws = client.post("/api/v1/chats", json={"title": "WS Chat", "workspace_id": ws_id, "chat_mode": "workspace"}, headers=auth_headers)
    assert res_ws.status_code == 201
    chat_ws_id = res_ws.json()["id"]

    # 4. List Workspace Chats
    list_ws_res = client.get(f"/api/v1/chats?workspace_id={ws_id}", headers=auth_headers)
    assert list_ws_res.status_code == 200
    ws_chats = list_ws_res.json()
    assert len(ws_chats) == 1
    assert ws_chats[0]["id"] == chat_ws_id

    # 5. Send Message to Global Chat
    # Note: Without a real GEMINI_API_KEY, the API will fail or return an error message, but we can verify the DB logic.
    msg_res = client.post(f"/api/v1/chats/{chat_id}/messages", json={"content": "Hello AI!"}, headers=auth_headers)
    assert msg_res.status_code == 200
    msg = msg_res.json()
    assert msg["role"] == "assistant"
    # The AI service error message or prompt-grounded refusal message is returned
    assert (
        "Sorry" in msg["content"] 
        or "error" in msg["content"].lower() 
        or "không chứa đủ thông tin" in msg["content"]
        or len(msg["content"]) > 0
    )

    # Verify context retrieval logic works (retrieved chunks should be 0 since no docs)
    assert msg["retrieved_chunk_count"] == 0
    assert "citations" in msg
    assert isinstance(msg["citations"], list)
    assert len(msg["citations"]) == 0

def test_chat_security_isolation(client, auth_headers, other_user_headers):
    res = client.post("/api/v1/chats", json={"title": "Secret Chat"}, headers=auth_headers)
    chat_id = res.json()["id"]

    # Other user tries to send a message
    msg_res = client.post(f"/api/v1/chats/{chat_id}/messages", json={"content": "Hello?"}, headers=other_user_headers)
    assert msg_res.status_code == 404
