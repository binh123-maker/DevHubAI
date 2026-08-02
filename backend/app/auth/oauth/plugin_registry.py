from typing import NamedTuple
from app.auth.interfaces.oauth import IOAuthProvider


class ProviderMetadata(NamedTuple):
    name: str
    display_name: str
    icon_name: str
    priority: int
    enabled: bool = True


class OAuthPluginRegistry:
    """Dynamic OAuth Provider Plugin Registry.
    
    Manages OAuth provider plugins with dynamic auto-registration, priority sorting,
    validation, and metadata inspection.
    """

    def __init__(self) -> None:
        self._providers: dict[str, IOAuthProvider] = {}
        self._metadata: dict[str, ProviderMetadata] = {}

    def register_plugin(self, provider: IOAuthProvider, metadata: ProviderMetadata) -> None:
        """Registers an OAuth Provider Plugin with associated metadata."""
        key = provider.provider_name.lower()
        self._providers[key] = provider
        self._metadata[key] = metadata

    def get_provider(self, name: str) -> IOAuthProvider | None:
        """Retrieves a registered provider plugin by name if enabled."""
        key = name.lower()
        meta = self._metadata.get(key)
        if meta and meta.enabled:
            return self._providers.get(key)
        return None

    def list_active_providers(self) -> list[ProviderMetadata]:
        """Lists active provider metadata sorted by priority."""
        active = [meta for meta in self._metadata.values() if meta.enabled]
        return sorted(active, key=lambda m: m.priority)


plugin_registry = OAuthPluginRegistry()
