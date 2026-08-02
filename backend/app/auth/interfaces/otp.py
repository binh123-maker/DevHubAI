from abc import ABC, abstractmethod
from enum import Enum
from typing import NamedTuple


class OTPPurpose(str, Enum):
    REGISTER = "register"
    PASSWORD_RESET = "password_reset"
    EMAIL_CHANGE = "email_change"
    ACCOUNT_DELETE = "account_delete"
    TWO_FACTOR_AUTH = "two_factor_auth"


class OTPResult(NamedTuple):
    success: bool
    message: str
    remaining_attempts: int | None = None
    cooldown_seconds: int | None = None


class IOTPService(ABC):
    """Abstract Base Class for OTP generation, storage, cooldown tracking, and verification."""

    @abstractmethod
    def generate_otp(self, target: str, purpose: OTPPurpose, length: int = 6, ttl_minutes: int = 10) -> str:
        """Generates a secure numeric OTP code for a target recipient (email/phone)."""
        pass

    @abstractmethod
    def verify_otp(self, target: str, purpose: OTPPurpose, code: str) -> OTPResult:
        """Validates the OTP code against target and purpose, enforcing max attempts and expiration."""
        pass

    @abstractmethod
    def invalidate_otp(self, target: str, purpose: OTPPurpose) -> None:
        """Explicitly revokes an active OTP code after successful consumption."""
        pass
