from datetime import datetime, timedelta, timezone
import hashlib
import logging
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.auth.config import auth_config
from app.auth.security.code_generator import VerificationCodeGenerator
from app.models.verification_code import VerificationCode
from app.services.auth_service import AuthError

logger = logging.getLogger(__name__)


class OTPService:
    """Enterprise OTP Engine & Verification Token Architecture Service (Parts 2, 9, 16, 24, 25)."""

    @staticmethod
    def generate_otp(db: Session, email: str, purpose: str, user_id: UUID | None = None) -> tuple[str, int]:
        """Generates a 6-digit OTP code, enforces rate limits and cooldown, and persists hashed record."""
        now = datetime.now(timezone.utc)
        clean_email = email.strip().lower()

        # 1. Rate Limit per Email (Part 24): Max 5 OTPs per hour
        one_hour_ago = now - timedelta(hours=1)
        recent_count = db.scalar(
            select(func.count()).select_from(VerificationCode).where(
                VerificationCode.email == clean_email,
                VerificationCode.purpose == purpose,
                VerificationCode.created_at >= one_hour_ago,
            )
        ) or 0

        if recent_count >= 5:
            raise AuthError("Bạn đã vượt quá số lần yêu cầu OTP tối đa trong 1 giờ (Tối đa 5 lần). Vui lòng thử lại sau.", status_code=429)

        # 2. Cooldown check (60 seconds)
        latest_code = db.scalar(
            select(VerificationCode)
            .where(
                VerificationCode.email == clean_email,
                VerificationCode.purpose == purpose,
            )
            .order_by(VerificationCode.created_at.desc())
        )

        if latest_code:
            elapsed = (now - latest_code.created_at).total_seconds()
            if elapsed < auth_config.otp_cooldown_seconds:
                remaining_cooldown = int(auth_config.otp_cooldown_seconds - elapsed)
                raise AuthError(f"Vui lòng đợi {remaining_cooldown} giây trước khi yêu cầu mã mới.", status_code=429)

        # 3. Revoke existing active codes for this email and purpose
        active_codes = db.scalars(
            select(VerificationCode).where(
                VerificationCode.email == clean_email,
                VerificationCode.purpose == purpose,
                VerificationCode.verified_at.is_(None),
                VerificationCode.revoked_at.is_(None),
            )
        ).all()
        for c in active_codes:
            c.revoked_at = now

        # 4. Generate 6-digit numeric OTP code
        raw_code = VerificationCodeGenerator.generate_numeric_otp(auth_config.otp_length)
        code_hash = hashlib.sha256(f"{clean_email}:{raw_code}".encode()).hexdigest()
        expires_at = now + timedelta(minutes=auth_config.otp_expire_minutes)

        code_record = VerificationCode(
            user_id=user_id,
            email=clean_email,
            purpose=purpose,
            code_hash=code_hash,
            max_attempts=auth_config.max_otp_attempts,
            attempt_count=0,
            expires_at=expires_at,
        )
        db.add(code_record)
        db.commit()
        db.refresh(code_record)

        logger.info(f"[OTPService] Generated OTP for email={clean_email}, purpose={purpose}, expires_at={expires_at}")
        return raw_code, auth_config.otp_cooldown_seconds

    @staticmethod
    def verify_otp(db: Session, email: str, purpose: str, code: str) -> str:
        """Verifies OTP code and generates single-use cryptographically secure Reset Token (Part 16)."""
        now = datetime.now(timezone.utc)
        clean_email = email.strip().lower()
        target_hash = hashlib.sha256(f"{clean_email}:{code.strip()}".encode()).hexdigest()

        active_record = db.scalar(
            select(VerificationCode)
            .where(
                VerificationCode.email == clean_email,
                VerificationCode.purpose == purpose,
                VerificationCode.verified_at.is_(None),
                VerificationCode.revoked_at.is_(None),
                VerificationCode.expires_at > now,
            )
            .order_by(VerificationCode.created_at.desc())
        )

        if not active_record:
            raise AuthError("Mã OTP không hợp lệ hoặc đã hết hạn.", status_code=400)

        # Check maximum failed attempt limit (Part 9)
        if active_record.attempt_count >= active_record.max_attempts:
            active_record.revoked_at = now
            db.commit()
            raise AuthError("Mã OTP đã vượt quá số lần thử tối đa. Vui lòng yêu cầu mã mới.", status_code=400)

        # Verify hash match
        if active_record.code_hash != target_hash:
            active_record.attempt_count += 1
            remaining = active_record.max_attempts - active_record.attempt_count
            db.commit()
            if remaining <= 0:
                active_record.revoked_at = now
                db.commit()
                raise AuthError("Mã OTP đã vượt quá số lần thử tối đa. Vui lòng yêu cầu mã mới.", status_code=400)
            raise AuthError(f"Mã OTP không chính xác. Còn {remaining} lần thử.", status_code=400)

        # Mark OTP as verified
        active_record.verified_at = now

        # Generate single-use Reset Token (Part 16)
        raw_reset_token = VerificationCodeGenerator.generate_url_safe_token(32)
        active_record.token_hash = hashlib.sha256(raw_reset_token.encode()).hexdigest()

        db.commit()
        logger.info(f"[OTPService] OTP verified for email={clean_email}, issued reset token.")
        return raw_reset_token

    @staticmethod
    def verify_reset_token(db: Session, email: str, reset_token: str) -> VerificationCode:
        """Validates single-use reset token hash and returns the verification record (Part 16)."""
        now = datetime.now(timezone.utc)
        clean_email = email.strip().lower()
        token_hash = hashlib.sha256(reset_token.strip().encode()).hexdigest()

        record = db.scalar(
            select(VerificationCode).where(
                VerificationCode.email == clean_email,
                VerificationCode.token_hash == token_hash,
                VerificationCode.verified_at.isnot(None),
                VerificationCode.revoked_at.is_(None),
                VerificationCode.expires_at > now,
            )
        )

        if not record:
            raise AuthError("Token khôi phục không hợp lệ hoặc đã hết hạn. Vui lòng thực hiện lại từ đầu.", status_code=400)

        return record

    @staticmethod
    def revoke_reset_token(db: Session, record: VerificationCode) -> None:
        """Revokes reset token after successful password update (Part 16)."""
        record.revoked_at = datetime.now(timezone.utc)
        db.commit()

    @staticmethod
    def cleanup_expired_codes(db: Session) -> int:
        """Cleanup service removing expired and revoked OTPs/Tokens (Part 17)."""
        now = datetime.now(timezone.utc)
        expired_records = db.scalars(
            select(VerificationCode).where(
                (VerificationCode.expires_at < now) | (VerificationCode.revoked_at.isnot(None))
            )
        ).all()

        count = len(expired_records)
        for r in expired_records:
            db.delete(r)
        db.commit()
        logger.info(f"[OTPService] Cleaned up {count} expired/revoked verification code records.")
        return count
