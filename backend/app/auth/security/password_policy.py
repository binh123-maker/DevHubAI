import re
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.config import auth_config
from app.auth.security.password import verify_password
from app.models.password_history import PasswordHistory
from app.models.user import User
class AuthError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def validate_password_policy(password: str) -> None:
    """Enforces strict enterprise password policy (Part 8).
    
    Requirements:
    - Min 8, max 128 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one numeric digit
    - At least one special character
    """
    if len(password) < auth_config.min_password_length:
        raise AuthError(f"Password must be at least {auth_config.min_password_length} characters long", status_code=400)

    if len(password) > auth_config.max_password_length:
        raise AuthError(f"Password cannot exceed {auth_config.max_password_length} characters", status_code=400)

    if auth_config.require_uppercase and not re.search(r"[A-Z]", password):
        raise AuthError("Password must contain at least one uppercase letter (A-Z)", status_code=400)

    if not re.search(r"[a-z]", password):
        raise AuthError("Password must contain at least one lowercase letter (a-z)", status_code=400)

    if auth_config.require_digit and not re.search(r"[0-9]", password):
        raise AuthError("Password must contain at least one numeric digit (0-9)", status_code=400)

    if auth_config.require_special_char and not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        raise AuthError("Password must contain at least one special character", status_code=400)


def check_password_history(db: Session, user: User, new_password: str, history_limit: int = 5) -> None:
    """Enforces Password History Policy (Part 18): Prevents reusing last N passwords."""
    # Check against user's current password hash
    if user.password_hash and verify_password(new_password, user.password_hash):
        raise AuthError("New password cannot be the same as your current password.", status_code=400)

    # Check against historical password hashes
    history_entries = list(
        db.scalars(
            select(PasswordHistory)
            .where(PasswordHistory.user_id == user.id)
            .order_by(PasswordHistory.created_at.desc())
            .limit(history_limit)
        ).all()
    )

    for entry in history_entries:
        if verify_password(new_password, entry.password_hash):
            raise AuthError("You cannot reuse a recently used password.", status_code=400)


def record_password_history(db: Session, user_id: UUID, old_password_hash: str, history_limit: int = 5) -> None:
    """Records old password hash in history and prunes entries beyond history_limit."""
    if not old_password_hash:
        return

    history_record = PasswordHistory(user_id=user_id, password_hash=old_password_hash)
    db.add(history_record)
    db.flush()

    # Retrieve all entries for user sorted by date
    all_history = list(
        db.scalars(
            select(PasswordHistory)
            .where(PasswordHistory.user_id == user_id)
            .order_by(PasswordHistory.created_at.desc())
        ).all()
    )

    if len(all_history) > history_limit:
        for excess in all_history[history_limit:]:
            db.delete(excess)
    db.commit()
