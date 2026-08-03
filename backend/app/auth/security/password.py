from app.core.security import get_password_hash, verify_password


def hash_password(password: str) -> str:
    """Hashes plain text password using bcrypt."""
    return get_password_hash(password)


__all__ = ["hash_password", "verify_password"]
