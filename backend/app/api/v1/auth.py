from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.oauth.google import google_provider
from app.auth.oauth.plugin_registry import plugin_registry
from app.auth.security.code_generator import VerificationCodeGenerator
from app.core.dependencies import CurrentUser, get_current_user_optional
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserProfileResponse
from app.services.auth_service import (
    AuthError,
    login_user,
    logout_user,
    refresh_access_token,
    register_user,
    to_user_response,
)
from app.services.oauth_service import OAuthAccountService

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]


class GoogleOAuthLoginUrlResponse(BaseModel):
    url: str
    state: str
    provider: str = "google"


class GoogleOAuthStatusResponse(BaseModel):
    connected: bool
    email: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    linked_at: str | None = None
    last_login_at: str | None = None
    can_disconnect: bool = True


def _handle_auth_error(error: AuthError) -> HTTPException:
    return HTTPException(status_code=error.status_code, detail=error.message)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: DbSession) -> TokenResponse:
    try:
        _, access_token, refresh_token = register_user(
            db,
            email=str(payload.email),
            password=payload.password,
            full_name=payload.full_name,
        )
    except AuthError as exc:
        raise _handle_auth_error(exc) from exc

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: DbSession) -> TokenResponse:
    try:
        _, access_token, refresh_token = login_user(
            db,
            email=str(payload.email),
            password=payload.password,
        )
    except AuthError as exc:
        raise _handle_auth_error(exc) from exc

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: RefreshTokenRequest, db: DbSession) -> TokenResponse:
    try:
        access_token, new_refresh_token = refresh_access_token(db, payload.refresh_token)
    except AuthError as exc:
        raise _handle_auth_error(exc) from exc

    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(payload: LogoutRequest, db: DbSession, _: CurrentUser) -> dict[str, str]:
    logout_user(db, payload.refresh_token)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserProfileResponse)
def get_me(current_user: CurrentUser) -> UserProfileResponse:
    return to_user_response(current_user)


# --- Google OAuth Endpoints (ADR 4 & ADR 5) ---

@router.get("/oauth/google/login", response_model=GoogleOAuthLoginUrlResponse)
def google_oauth_login_url(redirect_uri: str | None = Query(None)) -> GoogleOAuthLoginUrlResponse:
    """Generates authorization redirect URL and state token for Google OAuth 2.0."""
    target_redirect_uri = redirect_uri or settings.google_redirect_uri
    state = VerificationCodeGenerator.generate_url_safe_token(32)
    try:
        auth_url = google_provider.get_authorization_url(state=state, redirect_uri=target_redirect_uri)
    except AuthError as exc:
        raise _handle_auth_error(exc) from exc
    return GoogleOAuthLoginUrlResponse(url=auth_url, state=state, provider="google")


@router.get("/oauth/google/callback", response_model=TokenResponse)
async def google_oauth_callback(
    db: DbSession,
    code: str = Query(...),
    redirect_uri: str | None = Query(None),
    current_user: User | None = Depends(get_current_user_optional),
) -> TokenResponse:
    """Processes Google OAuth authorization code callback and returns DevHub JWT token pair."""
    target_redirect_uri = redirect_uri or settings.google_redirect_uri
    try:
        token_data = await google_provider.exchange_code_for_token(code=code, redirect_uri=target_redirect_uri)
        access_token_val = token_data.get("access_token")
        if not access_token_val:
            raise AuthError("No access_token returned by Google OAuth", status_code=502)

        user_info = await google_provider.fetch_user_info(access_token=access_token_val)
        _, access_token, refresh_token = OAuthAccountService.authenticate_oauth_user(
            db=db,
            info=user_info,
            current_authenticated_user=current_user,
        )
    except AuthError as exc:
        raise _handle_auth_error(exc) from exc

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.get("/oauth/google/status", response_model=GoogleOAuthStatusResponse)
def get_google_oauth_status(db: DbSession, current_user: CurrentUser) -> GoogleOAuthStatusResponse:
    """Returns current user's Google OAuth account status and details."""
    account = OAuthAccountService.get_user_google_account(db, current_user.id)
    has_password = current_user.password_hash is not None and len(current_user.password_hash) > 0

    if not account:
        return GoogleOAuthStatusResponse(
            connected=False,
            can_disconnect=has_password,
        )

    return GoogleOAuthStatusResponse(
        connected=True,
        email=account.email,
        display_name=account.display_name,
        avatar_url=account.avatar_url,
        linked_at=account.linked_at.isoformat(),
        last_login_at=account.last_login_at.isoformat(),
        can_disconnect=has_password,
    )


@router.post("/oauth/google/disconnect", status_code=status.HTTP_200_OK)
def disconnect_google_oauth(db: DbSession, current_user: CurrentUser) -> dict[str, str]:
    """Disconnects user's connected Google account enforcing Safe Disconnect Policy (ADR 5)."""
    try:
        OAuthAccountService.disconnect_google_account(db, current_user)
    except AuthError as exc:
        raise _handle_auth_error(exc) from exc
    return {"message": "Google account disconnected successfully"}

