"""DevHub AI Standalone Authentication Domain Module (Phase 1.5 Finalized Architecture)."""

from app.auth.config import AuthConfig, auth_config
from app.auth.constants.enums import (
    AuthProvider,
    OAuthStatus,
    OTPPurpose,
    SecurityEventType,
    SessionStatus,
    TokenType,
    UserState,
)
from app.auth.errors.codes import AUTH_ERROR_CATALOG, AuthErrorCode, AuthErrorSpec, ErrorSeverity
from app.auth.feature_flags import AuthFeatureFlags, auth_feature_flags
from app.auth.interfaces.audit import ISecurityLogger
from app.auth.interfaces.mail import IMailService
from app.auth.interfaces.oauth import IOAuthProvider, OAuthUserInfo
from app.auth.interfaces.otp import IOTPService, OTPResult
from app.auth.interfaces.rate_limit import IRateLimit
from app.auth.interfaces.session import ISessionManager
from app.auth.interfaces.token import ITokenManager
from app.auth.mail.templates import MailTemplateType
from app.auth.oauth.base import OAuthProviderRegistry, oauth_registry
from app.auth.oauth.plugin_registry import OAuthPluginRegistry, ProviderMetadata, plugin_registry
from app.auth.schemas.responses import StandardAuthResponse
from app.auth.security.code_generator import VerificationCodeGenerator
from app.auth.state_machine.account_state import AccountState, AccountStateMachine

__all__ = [
    "AuthConfig",
    "auth_config",
    "AuthFeatureFlags",
    "auth_feature_flags",
    "AuthProvider",
    "TokenType",
    "OTPPurpose",
    "SessionStatus",
    "UserState",
    "OAuthStatus",
    "SecurityEventType",
    "AuthErrorCode",
    "AuthErrorSpec",
    "ErrorSeverity",
    "AUTH_ERROR_CATALOG",
    "StandardAuthResponse",
    "OAuthPluginRegistry",
    "ProviderMetadata",
    "plugin_registry",
    "IOAuthProvider",
    "OAuthUserInfo",
    "IOTPService",
    "OTPResult",
    "IMailService",
    "ISessionManager",
    "ITokenManager",
    "ISecurityLogger",
    "IRateLimit",
    "VerificationCodeGenerator",
    "OAuthProviderRegistry",
    "oauth_registry",
    "AccountState",
    "AccountStateMachine",
    "MailTemplateType",
]
