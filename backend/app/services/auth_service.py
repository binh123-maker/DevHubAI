from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token_value,
    get_password_hash,
    hash_token,
    verify_password,
)
from app.models.enums import OAuthProvider
from app.models.user import RefreshToken, User, UserProfile
from app.schemas.user import UserProfileResponse


class AuthError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def to_user_response(user: User) -> UserProfileResponse:
    profile = user.profile
    return UserProfileResponse(
        id=user.id,
        email=user.email,
        role=user.role.value,
        full_name=profile.full_name if profile else "",
        avatar_url=profile.avatar_url if profile else None,
        gender=profile.gender.value if profile else "prefer_not_to_say",
    )


def _store_refresh_token(db: Session, user_id) -> str:
    refresh_token_value = create_refresh_token_value()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    db.add(
        RefreshToken(
            user_id=user_id,
            token_hash=hash_token(refresh_token_value),
            expires_at=expires_at,
        )
    )
    return refresh_token_value


def _issue_token_pair(db: Session, user: User) -> tuple[str, str]:
    access_token = create_access_token(str(user.id))
    refresh_token = _store_refresh_token(db, user.id)
    return access_token, refresh_token


def register_user(db: Session, email: str, password: str, full_name: str) -> tuple[User, str, str]:
    normalized_email = email.strip().lower()
    existing = db.scalar(select(User).where(User.email == normalized_email))
    if existing:
        raise AuthError("Email already registered", status_code=409)

    user = User(
        email=normalized_email,
        password_hash=get_password_hash(password),
        oauth_provider=OAuthProvider.LOCAL,
    )
    profile = UserProfile(user=user, full_name=full_name.strip())
    db.add(user)
    db.add(profile)

    try:
        db.flush()
        access_token, refresh_token = _issue_token_pair(db, user)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AuthError("Email already registered", status_code=409) from exc

    db.refresh(user)
    return user, access_token, refresh_token


def login_user(db: Session, email: str, password: str) -> tuple[User, str, str]:
    normalized_email = email.strip().lower()
    user = db.scalar(
        select(User).options(joinedload(User.profile)).where(User.email == normalized_email)
    )
    if user is None or user.password_hash is None or not verify_password(password, user.password_hash):
        raise AuthError("Invalid email or password", status_code=401)

    if not user.is_active:
        raise AuthError("Account is inactive", status_code=403)

    user.last_login_at = datetime.now(timezone.utc)
    access_token, refresh_token = _issue_token_pair(db, user)
    db.commit()
    db.refresh(user)
    return user, access_token, refresh_token


def refresh_access_token(db: Session, refresh_token: str) -> tuple[str, str]:
    token_hash = hash_token(refresh_token)
    record = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    now = datetime.now(timezone.utc)

    if record is None or record.revoked_at is not None or record.expires_at < now:
        raise AuthError("Invalid or expired refresh token", status_code=401)

    record.revoked_at = now
    access_token = create_access_token(str(record.user_id))
    new_refresh_token = _store_refresh_token(db, record.user_id)
    db.commit()
    return access_token, new_refresh_token


def logout_user(db: Session, refresh_token: str) -> None:
    token_hash = hash_token(refresh_token)
    record = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    if record is None or record.revoked_at is not None:
        return

    record.revoked_at = datetime.now(timezone.utc)
    db.commit()
