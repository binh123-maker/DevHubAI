from enum import Enum
from typing import NamedTuple


class ErrorSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AuthErrorSpec(NamedTuple):
    code: str
    http_status: int
    user_message: str
    developer_message: str
    severity: ErrorSeverity = ErrorSeverity.WARNING
    recoverable: bool = True


class AuthErrorCode(str, Enum):
    # --- LOGIN & CREDENTIAL ERRORS ---
    AUTH_LOGIN_001 = "AUTH_LOGIN_001"  # Invalid credentials
    AUTH_LOGIN_002 = "AUTH_LOGIN_002"  # Password incorrect
    AUTH_LOGIN_003 = "AUTH_LOGIN_003"  # Account locked due to failed attempts
    AUTH_LOGIN_004 = "AUTH_LOGIN_004"  # Account inactive or suspended

    # --- TOKEN ERRORS ---
    AUTH_TOKEN_001 = "AUTH_TOKEN_001"  # Access token expired
    AUTH_TOKEN_002 = "AUTH_TOKEN_002"  # Access token invalid or malformed
    AUTH_TOKEN_003 = "AUTH_TOKEN_003"  # Refresh token expired
    AUTH_TOKEN_004 = "AUTH_TOKEN_004"  # Refresh token revoked or reused

    # --- SESSION ERRORS ---
    AUTH_SESSION_001 = "AUTH_SESSION_001"  # Session expired
    AUTH_SESSION_002 = "AUTH_SESSION_002"  # Session revoked

    # --- OTP ERRORS ---
    AUTH_OTP_001 = "AUTH_OTP_001"  # OTP code expired
    AUTH_OTP_002 = "AUTH_OTP_002"  # OTP code invalid
    AUTH_OTP_003 = "AUTH_OTP_003"  # OTP attempts threshold exceeded
    AUTH_OTP_004 = "AUTH_OTP_004"  # OTP cooldown active

    # --- PROVIDER & OAUTH ERRORS ---
    AUTH_PROVIDER_001 = "AUTH_PROVIDER_001"  # Provider disabled
    AUTH_PROVIDER_002 = "AUTH_PROVIDER_002"  # Provider code exchange failed

    # --- ACCOUNT ERRORS ---
    AUTH_ACCOUNT_001 = "AUTH_ACCOUNT_001"  # Duplicate email address
    AUTH_ACCOUNT_002 = "AUTH_ACCOUNT_002"  # Password complexity mismatch
    AUTH_ACCOUNT_003 = "AUTH_ACCOUNT_003"  # Unauthorized access attempt


AUTH_ERROR_CATALOG: dict[AuthErrorCode, AuthErrorSpec] = {
    AuthErrorCode.AUTH_LOGIN_001: AuthErrorSpec(
        code="AUTH_LOGIN_001",
        http_status=401,
        user_message="Invalid email or password.",
        developer_message="Authentication failed due to incorrect user credentials.",
        severity=ErrorSeverity.WARNING,
        recoverable=True,
    ),
    AuthErrorCode.AUTH_LOGIN_003: AuthErrorSpec(
        code="AUTH_LOGIN_003",
        http_status=423,
        user_message="Account locked due to excessive failed login attempts. Try again later.",
        developer_message="Account locked after reaching max_login_attempts threshold.",
        severity=ErrorSeverity.CRITICAL,
        recoverable=False,
    ),
    AuthErrorCode.AUTH_TOKEN_001: AuthErrorSpec(
        code="AUTH_TOKEN_001",
        http_status=401,
        user_message="Your session has expired. Please sign in again.",
        developer_message="JWT access token payload signature or 'exp' claim validation failed.",
        severity=ErrorSeverity.INFO,
        recoverable=True,
    ),
    AuthErrorCode.AUTH_ACCOUNT_001: AuthErrorSpec(
        code="AUTH_ACCOUNT_001",
        http_status=409,
        user_message="This email address is already registered.",
        developer_message="Attempted to register an email address that exists in the database.",
        severity=ErrorSeverity.WARNING,
        recoverable=True,
    ),
}
