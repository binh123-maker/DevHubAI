from abc import ABC, abstractmethod
from typing import Any


class ITokenManager(ABC):
    """Abstract Base Class for JWT and refresh token handling."""

    @abstractmethod
    def create_access_token(self, subject: str, extra_claims: dict[str, Any] | None = None) -> str:
        """Issues an encoded JWT access token."""
        pass

    @abstractmethod
    def decode_access_token(self, token: str) -> dict[str, Any]:
        """Decodes and validates a JWT access token signature and expiration."""
        pass

    @abstractmethod
    def generate_refresh_token() -> str:
        """Generates a secure random refresh token string."""
        pass

    @abstractmethod
    def hash_token(self, token: str) -> str:
        """Produces a cryptographic SHA-256 hash of a token string for secure DB storage."""
        pass
