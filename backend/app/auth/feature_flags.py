from pydantic import BaseModel, Field


class AuthFeatureFlags(BaseModel):
    """Centralized Authentication Feature Flag Architecture.
    
    Allows enabling or disabling authentication features dynamically
    without changing business logic code.
    """

    enable_email_login: bool = Field(
        default=True,
        description="Enable standard email and password authentication.",
    )
    enable_google_login: bool = Field(
        default=True,
        description="Enable Google OAuth 2.0 authentication.",
    )
    enable_github_login: bool = Field(
        default=True,
        description="Enable GitHub OAuth 2.0 authentication.",
    )
    enable_microsoft_login: bool = Field(
        default=False,
        description="Enable Microsoft OAuth 2.0 authentication.",
    )
    enable_otp: bool = Field(
        default=True,
        description="Enable One-Time Passcode verification engine.",
    )
    enable_remember_me: bool = Field(
        default=True,
        description="Enable persistent Remember Me login sessions.",
    )
    enable_captcha: bool = Field(
        default=False,
        description="Enable CAPTCHA validation on public auth endpoints.",
    )
    enable_account_linking: bool = Field(
        default=True,
        description="Enable multi-provider account linking.",
    )
    enable_login_history: bool = Field(
        default=True,
        description="Enable security login event history logging.",
    )
    enable_device_sessions: bool = Field(
        default=True,
        description="Enable active device session tracking and management.",
    )
    enable_two_factor: bool = Field(
        default=False,
        description="Enable Two-Factor Authentication (2FA).",
    )


auth_feature_flags = AuthFeatureFlags()
