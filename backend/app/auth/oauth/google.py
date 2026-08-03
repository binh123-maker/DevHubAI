from typing import Any
import urllib.parse
import httpx

from app.auth.interfaces.oauth import IOAuthProvider, OAuthUserInfo
from app.auth.oauth.plugin_registry import ProviderMetadata, plugin_registry
from app.core.config import settings
from app.services.auth_service import AuthError


class GoogleProvider(IOAuthProvider):
    """Google OAuth 2.0 Provider Implementation conforming to IOAuthProvider strategy."""

    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

    @property
    def provider_name(self) -> str:
        return "google"

    def get_authorization_url(self, state: str, redirect_uri: str) -> str:
        """Generates the Google OAuth authorization redirect URL."""
        if not settings.google_client_id:
            raise AuthError("Google OAuth Client ID is missing. Please set GOOGLE_CLIENT_ID.", status_code=500)

        params = {
            "client_id": settings.google_client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "select_account",
        }
        return f"{self.GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"

    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict[str, Any]:
        """Exchanges authorization code for Google access token."""
        if not settings.google_client_id or not settings.google_client_secret:
            raise AuthError("Google OAuth credentials are missing. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.", status_code=500)

        data = {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(self.GOOGLE_TOKEN_URL, data=data)
            if response.status_code != 200:
                raise AuthError("Failed to exchange authorization code with Google", status_code=502)
            return response.json()

    async def fetch_user_info(self, access_token: str) -> OAuthUserInfo:
        """Fetches Google user profile and validates identity claims.
        
        Identity-Only Policy: Access token is used strictly in-memory during this
        call and is immediately discarded afterwards.
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(self.GOOGLE_USERINFO_URL, headers=headers)
            if response.status_code != 200:
                raise AuthError("Failed to fetch user profile from Google", status_code=502)
            payload = response.json()

        email = payload.get("email", "").strip().lower()
        sub = payload.get("sub", "")
        email_verified = payload.get("email_verified", False)

        if not email or not sub:
            raise AuthError("Invalid identity claims received from Google", status_code=400)

        # Mandatory Google Account Validation Policy (Part 18)
        if not email_verified:
            raise AuthError("Unverified Google accounts are not permitted to log in", status_code=400)

        return OAuthUserInfo(
            provider="google",
            provider_user_id=sub,
            email=email,
            email_verified=email_verified,
            full_name=payload.get("name", "").strip() or email.split("@")[0],
            avatar_url=payload.get("picture"),
            raw_claims={
                "locale": payload.get("locale"),
                "picture": payload.get("picture"),
                "email_verified": email_verified,
                "given_name": payload.get("given_name"),
                "family_name": payload.get("family_name"),
                "hosted_domain": payload.get("hd"),
            },
        )


google_provider = GoogleProvider()

