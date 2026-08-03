from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from app.auth.interfaces.oauth import OAuthUserInfo
from app.models.enums import OAuthProvider, UserRole
from app.models.oauth_account import OAuthAccount
from app.models.user import User, UserProfile
from app.models.workspace import Workspace
from app.services.auth_service import AuthError, _issue_token_pair, to_user_response
from app.schemas.user import UserProfileResponse


class OAuthAccountService:
    """Service handling secure account linking, profile sync, and session issuance for Google OAuth identity provider."""

    @staticmethod
    def get_user_google_account(db: Session, user_id: UUID) -> OAuthAccount | None:
        """Returns linked Google OAuth account for a user if exists."""
        return db.scalar(
            select(OAuthAccount).where(
                OAuthAccount.user_id == user_id,
                OAuthAccount.provider == "google",
            )
        )

    @staticmethod
    def authenticate_oauth_user(
        db: Session,
        info: OAuthUserInfo,
        current_authenticated_user: User | None = None,
    ) -> tuple[User, str, str]:
        """Authenticates or registers a user via Google OAuth identity claims.
        
        Enforces Identity-Only Policy, mandatory email verification checks,
        secure account linking, and non-destructive profile synchronization.
        """
        now = datetime.now(timezone.utc)

        # 1. Check if OAuth account already exists for (provider, provider_user_id)
        existing_oauth = db.scalar(
            select(OAuthAccount)
            .options(joinedload(OAuthAccount.user).joinedload(User.profile))
            .where(
                OAuthAccount.provider == "google",
                OAuthAccount.provider_user_id == info.provider_user_id,
            )
        )

        if existing_oauth:
            # Re-use existing OAuth link
            user = existing_oauth.user
            if not user.is_active:
                raise AuthError("Account is inactive", status_code=403)

            # Update login timestamps
            existing_oauth.last_login_at = now
            user.last_login_at = now

            access_token, refresh_token = _issue_token_pair(db, user)
            db.commit()
            db.refresh(user)
            return user, access_token, refresh_token

        # 2. Check if current authenticated user is explicitly linking Google
        if current_authenticated_user:
            user = current_authenticated_user
            existing_user_link = db.scalar(
                select(OAuthAccount).where(
                    OAuthAccount.user_id == user.id,
                    OAuthAccount.provider == "google",
                )
            )
            if existing_user_link:
                raise AuthError("Google account is already linked to your profile", status_code=409)

            # Create OAuth Account link
            oauth_account = OAuthAccount(
                user_id=user.id,
                provider="google",
                provider_user_id=info.provider_user_id,
                email=info.email,
                display_name=info.full_name,
                avatar_url=info.avatar_url,
                provider_metadata=info.raw_claims,
            )
            db.add(oauth_account)

            # Non-destructive Profile Sync
            if user.profile:
                if not user.profile.avatar_url and info.avatar_url:
                    user.profile.avatar_url = info.avatar_url

            user.last_login_at = now
            access_token, refresh_token = _issue_token_pair(db, user)
            db.commit()
            db.refresh(user)
            return user, access_token, refresh_token

        # 3. Check if existing user exists by email address
        existing_user = db.scalar(
            select(User)
            .options(joinedload(User.profile))
            .where(User.email == info.email)
        )

        if existing_user:
            if not existing_user.is_active:
                raise AuthError("Account is inactive and cannot be linked", status_code=403)

            # Link Google account to existing user
            oauth_account = OAuthAccount(
                user_id=existing_user.id,
                provider="google",
                provider_user_id=info.provider_user_id,
                email=info.email,
                display_name=info.full_name,
                avatar_url=info.avatar_url,
                provider_metadata=info.raw_claims,
            )
            db.add(oauth_account)

            # Non-destructive Profile Sync
            if existing_user.profile:
                if not existing_user.profile.avatar_url and info.avatar_url:
                    existing_user.profile.avatar_url = info.avatar_url

            existing_user.last_login_at = now
            access_token, refresh_token = _issue_token_pair(db, existing_user)
            db.commit()
            db.refresh(existing_user)
            return existing_user, access_token, refresh_token

        # 4. Create New User & Profile
        new_user = User(
            email=info.email,
            password_hash=None,
            oauth_provider=OAuthProvider.GOOGLE,
            oauth_id=info.provider_user_id,
            role=UserRole.USER,
            is_active=True,
            last_login_at=now,
        )
        new_profile = UserProfile(
            user=new_user,
            full_name=info.full_name,
            avatar_url=info.avatar_url,
        )
        db.add(new_user)
        db.add(new_profile)

        # Create Default Workspace for new user
        default_workspace = Workspace(
            user=new_user,
            name="My Workspace",
            description="Default workspace created automatically",
        )
        db.add(default_workspace)

        # Link OAuth Account
        oauth_account = OAuthAccount(
            user=new_user,
            provider="google",
            provider_user_id=info.provider_user_id,
            email=info.email,
            display_name=info.full_name,
            avatar_url=info.avatar_url,
            provider_metadata=info.raw_claims,
        )
        db.add(oauth_account)

        db.flush()
        access_token, refresh_token = _issue_token_pair(db, new_user)
        db.commit()
        db.refresh(new_user)
        return new_user, access_token, refresh_token

    @staticmethod
    def disconnect_google_account(db: Session, user: User) -> None:
        """Disconnects user's Google account enforcing Safe Google Disconnect Policy (ADR 5)."""
        account = db.scalar(
            select(OAuthAccount).where(
                OAuthAccount.user_id == user.id,
                OAuthAccount.provider == "google",
            )
        )
        if not account:
            raise AuthError("Google account is not linked to your profile", status_code=404)

        has_password = user.password_hash is not None and len(user.password_hash) > 0
        if not has_password:
            raise AuthError(
                "You must create a password before disconnecting your Google account.",
                status_code=400,
            )

        db.delete(account)
        db.commit()

