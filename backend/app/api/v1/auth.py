from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUser
from app.db.session import get_db
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

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]


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
