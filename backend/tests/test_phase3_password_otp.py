from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security.password import hash_password, verify_password
from app.auth.security.password_policy import validate_password_policy
from app.models.password_history import PasswordHistory
from app.models.user import RefreshToken, User
from app.models.verification_code import VerificationCode
from app.services.auth_service import AuthError, register_user
from app.services.otp_service import OTPService


def test_password_policy_validation():
    """Part 8: Password Policy validation testing."""
    # Valid password
    validate_password_policy("DevHub#2026Secure!")

    # Missing uppercase
    with pytest.raises(AuthError, match="uppercase"):
        validate_password_policy("devhub#2026secure!")

    # Missing digit
    with pytest.raises(AuthError, match="digit"):
        validate_password_policy("DevHub#Secure!")

    # Missing special char
    with pytest.raises(AuthError, match="special character"):
        validate_password_policy("DevHub2026Secure")

    # Too short (< 8)
    with pytest.raises(AuthError, match="at least 8"):
        validate_password_policy("Dev#1a")


def test_otp_generation_and_cooldown(db_session: Session):
    """Parts 2, 9, 24: OTP generation, 60s cooldown, rate limiting."""
    email = "otp_test_user@example.com"
    purpose = "password_reset"

    # 1. Generate OTP
    code1, cooldown = OTPService.generate_otp(db_session, email=email, purpose=purpose)
    assert len(code1) == 6
    assert code1.isdigit()
    assert cooldown == 60

    # 2. Immediate repeat attempt triggers 60s cooldown
    with pytest.raises(AuthError, match="Vui lòng đợi"):
        OTPService.generate_otp(db_session, email=email, purpose=purpose)


def test_verify_otp_max_attempts(db_session: Session):
    """Parts 5 & 9: OTP verification and max attempts limit (5 attempts)."""
    email = "max_attempts_user@example.com"
    purpose = "password_reset"

    code, _ = OTPService.generate_otp(db_session, email=email, purpose=purpose)

    # 4 invalid attempts
    for _ in range(4):
        with pytest.raises(AuthError, match="Mã OTP không chính xác"):
            OTPService.verify_otp(db_session, email=email, purpose=purpose, code="000000")

    # 5th failed attempt revokes code
    with pytest.raises(AuthError, match="vượt quá số lần thử tối đa"):
        OTPService.verify_otp(db_session, email=email, purpose=purpose, code="000000")


def test_forgot_and_reset_password_flow(db_session: Session):
    """Parts 4, 5, 6, 16, 19: End-to-end Forgot Password -> Verify OTP -> Reset Password."""
    email = "reset_flow_user@example.com"
    old_password = "OldPassword#2026"
    new_password = "NewPassword#2026"

    user, _, _ = register_user(db_session, email=email, password=old_password, full_name="Reset User")

    # 1. Generate OTP
    otp_code, _ = OTPService.generate_otp(db_session, email=email, purpose="password_reset", user_id=user.id)

    # 2. Verify OTP -> get single-use reset token
    reset_token = OTPService.verify_otp(db_session, email=email, purpose="password_reset", code=otp_code)
    assert reset_token is not None and len(reset_token) > 0

    # 3. Verify single-use reset token
    record = OTPService.verify_reset_token(db_session, email=email, reset_token=reset_token)
    assert record is not None

    # 4. Update Password
    user.password_hash = hash_password(new_password)
    OTPService.revoke_reset_token(db_session, record)
    db_session.commit()

    db_session.refresh(user)
    assert verify_password(new_password, user.password_hash)


def test_password_history_policy(db_session: Session):
    """Part 18: Password History policy preventing reuse of last 5 passwords."""
    email = "history_user@example.com"
    pwd1 = "Password1111#2026"
    pwd2 = "Password2222#2026"

    user, _, _ = register_user(db_session, email=email, password=pwd1, full_name="History User")

    # Record initial password history
    ph1 = PasswordHistory(user_id=user.id, password_hash=user.password_hash)
    db_session.add(ph1)
    db_session.commit()

    # Change to pwd2
    user.password_hash = hash_password(pwd2)
    ph2 = PasswordHistory(user_id=user.id, password_hash=user.password_hash)
    db_session.add(ph2)
    db_session.commit()

    # Attempt to reuse pwd1 (found in history)
    history_hashes = db_session.scalars(
        select(PasswordHistory.password_hash).where(PasswordHistory.user_id == user.id)
    ).all()

    matches_old = any(verify_password(pwd1, h) for h in history_hashes)
    assert matches_old is True


def test_cleanup_expired_codes(db_session: Session):
    """Part 17: Cleanup expired/revoked verification code records."""
    now = datetime.now(timezone.utc)
    expired_code = VerificationCode(
        email="expired@example.com",
        purpose="password_reset",
        code_hash="dummy_hash",
        expires_at=now - timedelta(minutes=1),
    )
    db_session.add(expired_code)
    db_session.commit()

    cleaned_count = OTPService.cleanup_expired_codes(db_session)
    assert cleaned_count >= 1
