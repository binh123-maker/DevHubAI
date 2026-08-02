from app.auth.interfaces.oauth import IOAuthProvider, OAuthUserInfo


class OAuthProviderRegistry:
    """Registry pattern managing OAuth Provider instances."""

    def __init__(self) -> None:
        self._providers: dict[str, IOAuthProvider] = {}

    def register(self, provider: IOAuthProvider) -> None:
        """Registers an OAuth provider implementation."""
        self._providers[provider.provider_name.lower()] = provider

    def get(self, name: str) -> IOAuthProvider | None:
        """Retrieves a provider by name."""
        return self._providers.get(name.lower())

    def list_providers(self) -> list[str]:
        """Lists registered provider names."""
        return list(self._providers.keys())


oauth_registry = OAuthProviderRegistry()
