from typing import Literal
from pydantic import BaseModel, Field

from app.core.config import settings


class AuthConfig(BaseModel):
    """Centralized Authentication Configuration Center.
    
    Provides a single typed access point for all authentication parameters,
    wrapping underlying environment settings and categorizing parameters.
    """

    # --- Token Expiration Settings ---
    access_token_expire_minutes: int = Field(
        default_factory=lambda: settings.access_token_expire_minutes,
        description="Lifetime of access token in minutes. Category: SECURITY_CRITICAL",
    )
    refresh_token_expire_days: int = Field(
        default_factory=lambda: settings.refresh_token_expire_days,
        description="Lifetime of refresh token in days. Category: SECURITY_CRITICAL",
    )

    # --- OTP & Verification Settings ---
    otp_expire_minutes: int = Field(
        default=10,
        description="Lifetime of OTP verification codes in minutes. Category: SECURITY_CRITICAL",
    )
    otp_length: int = Field(
        default=6,
        description="Length of numeric OTP codes. Category: PRODUCTION",
    )
    max_otp_attempts: int = Field(
        default=5,
        description="Maximum failed OTP attempts before lockout. Category: SECURITY_CRITICAL",
    )
    otp_cooldown_seconds: int = Field(
        default=60,
        description="Minimum cooldown interval between OTP resends in seconds. Category: PRODUCTION",
    )

    # --- Password Policy Settings ---
    min_password_length: int = Field(
        default=8,
        description="Minimum password length. Category: SECURITY_CRITICAL",
    )
    max_password_length: int = Field(
        default=128,
        description="Maximum password length. Category: PRODUCTION",
    )
    require_uppercase: bool = Field(
        default=True,
        description="Enforce uppercase character requirement. Category: SECURITY_CRITICAL",
    )
    require_digit: bool = Field(
        default=True,
        description="Enforce numeric digit requirement. Category: SECURITY_CRITICAL",
    )
    require_special_char: bool = Field(
        default=True,
        description="Enforce special character requirement. Category: SECURITY_CRITICAL",
    )

    # --- Session & Brute-Force Limits ---
    max_login_attempts: int = Field(
        default=5,
        description="Maximum failed login attempts before account lockout. Category: SECURITY_CRITICAL",
    )
    session_idle_timeout_days: int = Field(
        default=30,
        description="Idle session lifetime in days. Category: PRODUCTION",
    )
    remember_me_expire_days: int = Field(
        default=30,
        description="Remember me token duration in days. Category: OPTIONAL",
    )

    # --- Rate Limiting Defaults ---
    rate_limit_login_per_minute: int = Field(
        default=10,
        description="Maximum login attempts per minute per IP. Category: SECURITY_CRITICAL",
    )
    rate_limit_register_per_hour: int = Field(
        default=5,
        description="Maximum register attempts per hour per IP. Category: SECURITY_CRITICAL",
    )

    # --- Cookie Settings ---
    cookie_secure: bool = Field(
        default=False,
        description="Set Secure flag on auth cookies (True in production). Category: PRODUCTION",
    )
    cookie_httponly: bool = Field(
        default=True,
        description="Set HttpOnly flag on auth cookies. Category: SECURITY_CRITICAL",
    )
    cookie_samesite: Literal["lax", "strict", "none"] = Field(
        default="lax",
        description="SameSite cookie policy. Category: SECURITY_CRITICAL",
    )


auth_config = AuthConfig()
