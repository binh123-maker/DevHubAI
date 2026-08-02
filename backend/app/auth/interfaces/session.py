from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID


class ISessionManager(ABC):
    """Abstract Base Class for user session lifecycle and device tracking."""

    @abstractmethod
    def create_session(
        self,
        user_id: UUID,
        ip_address: str | None = None,
        user_agent: str | None = None,
        device_name: str | None = None,
    ) -> str:
        """Creates a new active session record and returns the session token."""
        pass

    @abstractmethod
    def revoke_session(self, session_id: UUID) -> bool:
        """Revokes a specific session by ID."""
        pass

    @abstractmethod
    def revoke_all_user_sessions(self, user_id: UUID, except_session_id: UUID | None = None) -> int:
        """Revokes all active sessions for a user (e.g. on password reset or remote logout)."""
        pass
