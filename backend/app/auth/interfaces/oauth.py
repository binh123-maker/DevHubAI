from abc import ABC, abstractmethod
from typing import Any, NamedTuple


class OAuthUserInfo(NamedTuple):
    provider: str
    provider_user_id: str
    email: str
    email_verified: bool
    full_name: str
    avatar_url: str | None
    raw_claims: dict[str, Any]


class IOAuthProvider(ABC):
    """Abstract Base Class for OAuth 2.0 / OpenID Connect Providers (Google, GitHub, etc.)."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the identifier name of the provider (e.g. 'google', 'github')."""
        pass

    @abstractmethod
    def get_authorization_url(self, state: str, redirect_uri: str) -> str:
        """Generates the authorization redirect URL for initiating the OAuth flow."""
        pass

    @abstractmethod
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict[str, Any]:
        """Exchanges an authorization code for an OAuth access token and id_token."""
        pass

    @abstractmethod
    async def fetch_user_info(self, access_token: str) -> OAuthUserInfo:
        """Fetches and normalizes user profile information from the provider."""
        pass
