from enum import Enum


class AuthProvider(str, Enum):
    LOCAL = "local"
    EMAIL = "email"
    GOOGLE = "google"


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    VERIFICATION = "verification"
    RESET = "reset"


class OTPPurpose(str, Enum):
    REGISTER = "register"
    PASSWORD_RESET = "password_reset"
    EMAIL_CHANGE = "email_change"
    ACCOUNT_DELETE = "account_delete"
    TWO_FACTOR = "two_factor"


class SessionStatus(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    LOGGED_OUT = "logged_out"


class UserState(str, Enum):
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    ACTIVE = "active"
    LOCKED = "locked"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class OAuthStatus(str, Enum):
    REDIRECT = "redirect"
    AUTHORIZATION = "authorization"
    CALLBACK = "callback"
    TOKEN_EXCHANGE = "token_exchange"
    IDENTITY_VERIFICATION = "identity_verification"
    ACCOUNT_LINKING = "account_linking"
    COMPLETED = "completed"
    FAILED = "failed"


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
    SESSION_CREATED = "session_created"
    SESSION_REVOKED = "session_revoked"
    TOKEN_REFRESHED = "token_refreshed"
    ACCOUNT_LINKED = "account_linked"
    ACCOUNT_UNLINKED = "account_unlinked"

