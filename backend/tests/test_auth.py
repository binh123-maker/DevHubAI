def test_register_login_me_refresh_logout_flow(client):
    register_payload = {
        "email": "demo@devhub.ai",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
        "full_name": "Demo User",
    }

    register_response = client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == 201
    register_data = register_response.json()
    assert register_data["access_token"]
    assert register_data["refresh_token"]
    assert register_data["token_type"] == "bearer"

    access_token = register_data["access_token"]
    refresh_token = register_data["refresh_token"]
    auth_headers = {"Authorization": f"Bearer {access_token}"}

    me_response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == "demo@devhub.ai"
    assert me_data["full_name"] == "Demo User"
    assert me_data["role"] == "user"

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "demo@devhub.ai", "password": "SecurePass123!"},
    )
    assert login_response.status_code == 200
    login_refresh_token = login_response.json()["refresh_token"]

    refresh_response = client.post("/api/v1/auth/refresh", json={"refresh_token": login_refresh_token})
    assert refresh_response.status_code == 200
    rotated_refresh_token = refresh_response.json()["refresh_token"]
    assert rotated_refresh_token != login_refresh_token

    old_refresh_response = client.post("/api/v1/auth/refresh", json={"refresh_token": login_refresh_token})
    assert old_refresh_response.status_code == 401

    logout_response = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": rotated_refresh_token},
        headers=auth_headers,
    )
    assert logout_response.status_code == 200

    revoked_refresh_response = client.post("/api/v1/auth/refresh", json={"refresh_token": rotated_refresh_token})
    assert revoked_refresh_response.status_code == 401


def test_register_duplicate_email(client):
    payload = {
        "email": "duplicate@devhub.ai",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
        "full_name": "First User",
    }
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201

    duplicate_response = client.post("/api/v1/auth/register", json=payload)
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"] == "Email already registered"


def test_register_password_mismatch(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "mismatch@devhub.ai",
            "password": "SecurePass123!",
            "password_confirm": "DifferentPass!",
            "full_name": "Mismatch User",
        },
    )
    assert response.status_code == 422


def test_login_invalid_credentials(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "valid@devhub.ai",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "full_name": "Valid User",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "valid@devhub.ai", "password": "WrongPassword!"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_me_requires_authentication(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
