import urllib.parse
from unittest.mock import patch

import pytest
from app.auth.interfaces.oauth import OAuthUserInfo
from app.models.oauth_account import OAuthAccount
from app.models.user import User
from app.models.workspace import Workspace
from app.services.auth_service import AuthError


def test_google_oauth_login_url(client):
    with patch("app.core.config.settings.google_client_id", "test-client-id"):
        redirect_uri = "http://localhost:5173/auth/callback/google"
        response = client.get(f"/api/v1/auth/oauth/google/login?redirect_uri={urllib.parse.quote(redirect_uri)}")
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "state" in data
        assert data["provider"] == "google"
        assert "accounts.google.com" in data["url"]


def test_google_oauth_missing_config(client):
    with patch("app.core.config.settings.google_client_id", ""):
        response = client.get("/api/v1/auth/oauth/google/login")
        assert response.status_code == 500
        assert "missing" in response.json()["detail"].lower()


@patch("app.auth.oauth.google.GoogleProvider.exchange_code_for_token")
@patch("app.auth.oauth.google.GoogleProvider.fetch_user_info")
def test_first_google_login(mock_fetch_info, mock_exchange, client, db_session):
    """ADR 10: First Google Login - Verify User, Profile, Workspace, and OAuthAccount created."""
    mock_exchange.return_value = {"access_token": "fake-google-access-token"}
    mock_fetch_info.return_value = OAuthUserInfo(
        provider="google",
        provider_user_id="google-sub-1001",
        email="newuser@google.com",
        email_verified=True,
        full_name="New Google User",
        avatar_url="https://lh3.googleusercontent.com/photo.jpg",
        raw_claims={"locale": "en"},
    )

    redirect_uri = "http://localhost:5173/auth/callback/google"
    response = client.get(f"/api/v1/auth/oauth/google/callback?code=valid-code&redirect_uri={urllib.parse.quote(redirect_uri)}")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # 1. Verify User created
    created_user = db_session.query(User).filter(User.email == "newuser@google.com").first()
    assert created_user is not None
    assert created_user.password_hash is None

    # 2. Verify Profile created
    assert created_user.profile is not None
    assert created_user.profile.full_name == "New Google User"
    assert created_user.profile.avatar_url == "https://lh3.googleusercontent.com/photo.jpg"

    # 3. Verify Default Workspace created
    workspace = db_session.query(Workspace).filter(Workspace.user_id == created_user.id).first()
    assert workspace is not None
    assert workspace.name == "My Workspace"

    # 4. Verify OAuthAccount created
    oauth_account = db_session.query(OAuthAccount).filter(OAuthAccount.user_id == created_user.id).first()
    assert oauth_account is not None
    assert oauth_account.provider == "google"
    assert oauth_account.provider_user_id == "google-sub-1001"


@patch("app.auth.oauth.google.GoogleProvider.exchange_code_for_token")
@patch("app.auth.oauth.google.GoogleProvider.fetch_user_info")
def test_existing_google_user(mock_fetch_info, mock_exchange, client, db_session):
    """ADR 10: Existing Google User - Verify login succeeds with no duplicates."""
    mock_exchange.return_value = {"access_token": "fake-google-token"}
    user_info = OAuthUserInfo(
        provider="google",
        provider_user_id="google-sub-repeat",
        email="repeat@google.com",
        email_verified=True,
        full_name="Repeat User",
        avatar_url="https://lh3.googleusercontent.com/avatar.jpg",
        raw_claims={},
    )
    mock_fetch_info.return_value = user_info

    redirect_uri = "http://localhost:5173/auth/callback/google"
    # First login
    res1 = client.get(f"/api/v1/auth/oauth/google/callback?code=code1&redirect_uri={urllib.parse.quote(redirect_uri)}")
    assert res1.status_code == 200

    # Second login
    res2 = client.get(f"/api/v1/auth/oauth/google/callback?code=code2&redirect_uri={urllib.parse.quote(redirect_uri)}")
    assert res2.status_code == 200

    users_count = db_session.query(User).filter(User.email == "repeat@google.com").count()
    assert users_count == 1
    oauth_count = db_session.query(OAuthAccount).filter(OAuthAccount.provider_user_id == "google-sub-repeat").count()
    assert oauth_count == 1


@patch("app.auth.oauth.google.GoogleProvider.exchange_code_for_token")
@patch("app.auth.oauth.google.GoogleProvider.fetch_user_info")
def test_existing_email_user_linking(mock_fetch_info, mock_exchange, client, db_session):
    """ADR 10: Existing Email User - Verify automatic account linking."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "existing@devhub.ai",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "full_name": "Existing Email User",
        },
    )

    mock_exchange.return_value = {"access_token": "fake-google-token"}
    mock_fetch_info.return_value = OAuthUserInfo(
        provider="google",
        provider_user_id="google-sub-2002",
        email="existing@devhub.ai",
        email_verified=True,
        full_name="Existing Google User",
        avatar_url="https://lh3.googleusercontent.com/avatar.jpg",
        raw_claims={},
    )

    redirect_uri = "http://localhost:5173/auth/callback/google"
    response = client.get(f"/api/v1/auth/oauth/google/callback?code=valid-code&redirect_uri={urllib.parse.quote(redirect_uri)}")
    assert response.status_code == 200

    user = db_session.query(User).filter(User.email == "existing@devhub.ai").first()
    assert user is not None
    assert len(user.oauth_accounts) == 1
    assert user.oauth_accounts[0].provider_user_id == "google-sub-2002"


@patch("app.auth.oauth.google.GoogleProvider.exchange_code_for_token")
@patch("app.auth.oauth.google.GoogleProvider.fetch_user_info")
def test_unverified_google_email_rejection(mock_fetch_info, mock_exchange, client):
    """ADR 10: Unverified Google Email - Verify authentication rejected when email_verified is False."""
    mock_exchange.return_value = {"access_token": "fake-google-token"}
    mock_fetch_info.side_effect = AuthError("Unverified Google accounts are not permitted to log in", status_code=400)

    redirect_uri = "http://localhost:5173/auth/callback/google"
    response = client.get(f"/api/v1/auth/oauth/google/callback?code=unverified-code&redirect_uri={urllib.parse.quote(redirect_uri)}")
    assert response.status_code == 400
    assert "Unverified Google accounts" in response.json()["detail"]


def test_google_status_endpoint(client, db_session):
    """ADR 10: Status endpoint verification."""
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": "statususer@devhub.ai",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "full_name": "Status User",
        },
    ).json()
    headers = {"Authorization": f"Bearer {reg['access_token']}"}

    res = client.get("/api/v1/auth/oauth/google/status", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["connected"] is False
    assert data["can_disconnect"] is True


@patch("app.auth.oauth.google.GoogleProvider.exchange_code_for_token")
@patch("app.auth.oauth.google.GoogleProvider.fetch_user_info")
def test_google_disconnect_policy(mock_fetch_info, mock_exchange, client, db_session):
    """ADR 10: Safe Google Disconnect Policy - Reject disconnect when no local password exists."""
    # 1. User logs in via Google (no password)
    mock_exchange.return_value = {"access_token": "fake-google-token"}
    mock_fetch_info.return_value = OAuthUserInfo(
        provider="google",
        provider_user_id="google-sub-nopass",
        email="googleonly@devhub.ai",
        email_verified=True,
        full_name="Google Only User",
        avatar_url=None,
        raw_claims={},
    )
    redirect_uri = "http://localhost:5173/auth/callback/google"
    res_login = client.get(f"/api/v1/auth/oauth/google/callback?code=valid-code&redirect_uri={urllib.parse.quote(redirect_uri)}").json()
    headers = {"Authorization": f"Bearer {res_login['access_token']}"}

    # 2. Attempt disconnect - must fail with 400 because user has no password
    res_disc = client.post("/api/v1/auth/oauth/google/disconnect", headers=headers)
    assert res_disc.status_code == 400
    assert "must create a password" in res_disc.json()["detail"].lower()


def test_refresh_token_and_logout(client):
    """ADR 10: Refresh Token & Logout Flow."""
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": "tokenuser@devhub.ai",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "full_name": "Token User",
        },
    ).json()

    # Test Refresh
    res_ref = client.post("/api/v1/auth/refresh", json={"refresh_token": reg["refresh_token"]})
    assert res_ref.status_code == 200
    assert "access_token" in res_ref.json()

    # Test Logout
    headers = {"Authorization": f"Bearer {reg['access_token']}"}
    res_logout = client.post("/api/v1/auth/logout", json={"refresh_token": reg["refresh_token"]}, headers=headers)
    assert res_logout.status_code == 200
