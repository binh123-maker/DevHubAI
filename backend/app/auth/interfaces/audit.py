from abc import ABC, abstractmethod
from enum import Enum
from typing import Any
from uuid import UUID


class SecurityEventType(str, Enum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    REGISTER = "register"
    EMAIL_VERIFIED = "email_verified"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET = "password_reset"
    OTP_SENT = "otp_sent"
    OTP_VERIFIED = "otp_verified"
    GOOGLE_LOGIN = "google_login"
    GITHUB_LOGIN = "github_login"
    SESSION_CREATED = "session_created"
    SESSION_REVOKED = "session_revoked"
    TOKEN_REFRESHED = "token_refreshed"
    ACCOUNT_LINKED = "account_linked"
    ACCOUNT_UNLINKED = "account_unlinked"


class EventSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ISecurityLogger(ABC):
    """Abstract Base Class for auditing security events."""

    @abstractmethod
    def log_event(
        self,
        event_type: SecurityEventType,
        user_id: UUID | None,
        severity: EventSeverity = EventSeverity.INFO,
        ip_address: str | None = None,
        user_agent: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Records a security audit log entry."""
        pass
