import secrets
import string


class VerificationCodeGenerator:
    """Cryptographically secure generator for verification codes, OTPs, and tokens."""

    @staticmethod
    def generate_numeric_otp(digits: int = 6) -> str:
        """Generates a secure numeric string of specified length (e.g. '849201')."""
        return "".join(secrets.choice(string.digits) for _ in range(digits))

    @staticmethod
    def generate_alphanumeric_code(length: int = 32) -> str:
        """Generates a secure alphanumeric string (e.g. URL token / verification code)."""
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def generate_url_safe_token(bytes_count: int = 32) -> str:
        """Generates a URL-safe base64 secret token."""
        return secrets.token_urlsafe(bytes_count)
