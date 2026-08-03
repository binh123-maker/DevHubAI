from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.auth.oauth.google import google_provider
from app.auth.security.code_generator import VerificationCodeGenerator
from app.auth.security.password import hash_password, verify_password
from app.auth.security.password_policy import (
    check_password_history,
    record_password_history,
    validate_password_policy,
)
from app.core.config import settings
from app.core.dependencies import CurrentUser, get_current_user_optional
from app.db.session import get_db
from app.models.user import RefreshToken, User
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyOtpRequest,
    VerifyOtpResponse,
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
from app.services.mail_service import mail_service
from app.services.oauth_service import OAuthAccountService
from app.services.otp_service import OTPService


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


# --- Phase 3: Password Recovery & Management Endpoints ---

@router.post("/password/forgot", response_model=ForgotPasswordResponse, status_code=status.HTTP_200_OK)
async def forgot_password(payload: ForgotPasswordRequest, db: DbSession) -> ForgotPasswordResponse:
    """Initiates Password Recovery flow: generates 6-digit OTP code and dispatches email (Parts 4 & 9)."""
    clean_email = str(payload.email).strip().lower()
    user = db.scalar(select(User).where(User.email == clean_email))

    if not user:
        # Uniform response to prevent email enumeration attacks
        return ForgotPasswordResponse(
            message="Mã xác thực đã được gửi đến email của bạn nếu email tồn tại trong hệ thống.",
            cooldown_seconds=60,
        )

    try:
        raw_code, cooldown = OTPService.generate_otp(
            db=db,
            email=clean_email,
            purpose="password_reset",
            user_id=user.id,
        )
        full_name = user.profile.full_name if user.profile else user.email
        await mail_service.send_mail(
            to_email=clean_email,
            subject="Mã xác thực khôi phục mật khẩu DevHub AI",
            template_name="forgot_password",
            template_context={"full_name": full_name, "otp_code": raw_code, "ttl_minutes": 10},
        )
    except AuthError as exc:
        raise _handle_auth_error(exc) from exc

    return ForgotPasswordResponse(
        message="Mã xác thực đã được gửi đến email của bạn.",
        cooldown_seconds=cooldown,
    )


@router.post("/password/verify", response_model=VerifyOtpResponse, status_code=status.HTTP_200_OK)
def verify_otp(payload: VerifyOtpRequest, db: DbSession) -> VerifyOtpResponse:
    """Verifies OTP code and generates single-use cryptographically secure Reset Token (Parts 5 & 16)."""
    try:
        reset_token = OTPService.verify_otp(
            db=db,
            email=str(payload.email),
            purpose="password_reset",
            code=payload.code,
        )
    except AuthError as exc:
        raise _handle_auth_error(exc) from exc

    return VerifyOtpResponse(
        reset_token=reset_token,
        message="Mã OTP xác thực thành công.",
    )


@router.post("/password/reset", status_code=status.HTTP_200_OK)
async def reset_password(payload: ResetPasswordRequest, db: DbSession) -> dict[str, str]:
    """Resets password using single-use Reset Token, enforces Password Policy, revokes all sessions (Parts 6, 16, 18, 19)."""
    clean_email = str(payload.email).strip().lower()

    try:
        # 1. Verify Reset Token (Part 16)
        verification_record = OTPService.verify_reset_token(db=db, email=clean_email, reset_token=payload.reset_token)

        user = db.scalar(select(User).where(User.email == clean_email))
        if not user:
            raise AuthError("Tài khoản không tồn tại.", status_code=404)

        # 2. Enforce Password Policy & Password History (Parts 8 & 18)
        validate_password_policy(payload.new_password)
        check_password_history(db=db, user=user, new_password=payload.new_password)

        # 3. Record Old Password Hash in History (Part 18)
        if user.password_hash:
            record_password_history(db=db, user_id=user.id, old_password_hash=user.password_hash)

        # 4. Update Password Hash
        user.password_hash = hash_password(payload.new_password)

        # 5. Revoke Reset Token (Part 16)
        OTPService.revoke_reset_token(db=db, record=verification_record)

        # 6. Complete Session Revocation (Part 19): Revoke all refresh tokens
        db.execute(delete(RefreshToken).where(RefreshToken.user_id == user.id))
        db.commit()

        # 7. Security Alert Email (Part 23)
        full_name = user.profile.full_name if user.profile else user.email
        await mail_service.send_mail(
            to_email=clean_email,
            subject="Thông báo bảo mật: Mật khẩu DevHub AI đã được thay đổi",
            template_name="password_changed",
            template_context={"full_name": full_name},
        )
    except AuthError as exc:
        raise _handle_auth_error(exc) from exc

    return {"message": "Đặt lại mật khẩu thành công. Vui lòng đăng nhập lại bằng mật khẩu mới."}


@router.post("/password/change", status_code=status.HTTP_200_OK)
async def change_password(payload: ChangePasswordRequest, db: DbSession, current_user: CurrentUser) -> dict[str, str]:
    """Changes password for authenticated user, enforces current password validation and history policy (Parts 7, 8, 18, 19)."""
    try:
        # 1. Verify Current Password
        if current_user.password_hash:
            if not verify_password(payload.current_password, current_user.password_hash):
                raise AuthError("Mật khẩu hiện tại không chính xác.", status_code=400)

        # 2. Enforce Password Policy & Password History
        validate_password_policy(payload.new_password)
        check_password_history(db=db, user=current_user, new_password=payload.new_password)

        # 3. Record Old Password in History
        if current_user.password_hash:
            record_password_history(db=db, user_id=current_user.id, old_password_hash=current_user.password_hash)

        # 4. Update Password Hash
        current_user.password_hash = hash_password(payload.new_password)

        # 5. Revoke Refresh Tokens across all sessions
        db.execute(delete(RefreshToken).where(RefreshToken.user_id == current_user.id))
        db.commit()

        # 6. Dispatch Security Email Alert
        full_name = current_user.profile.full_name if current_user.profile else current_user.email
        await mail_service.send_mail(
            to_email=current_user.email,
            subject="Thông báo bảo mật: Mật khẩu DevHub AI đã được thay đổi",
            template_name="password_changed",
            template_context={"full_name": full_name},
        )
    except AuthError as exc:
        raise _handle_auth_error(exc) from exc

    return {"message": "Đổi mật khẩu thành công."}


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


