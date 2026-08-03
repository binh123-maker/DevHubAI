# DevHub AI - Password Reset & Verification Token Architecture (Phase 3)

## Overview
This document specifies the Password Reset flow and **Verification Token Architecture** implemented under Phase 3.

---

## Architectural Sequence

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Frontend as DevHub AI Frontend
    participant API as Auth API (/api/v1/auth/password)
    participant OTP as OTPService
    participant Mail as MailService
    participant DB as PostgreSQL DB

    User->>Frontend: Enter Email Address
    Frontend->>API: POST /password/forgot { email }
    API->>OTP: generate_otp(email, purpose="password_reset")
    OTP->>DB: Save VerificationCode (expires in 10m)
    API->>Mail: send_mail(to=email, template="forgot_password")
    API-->>Frontend: 200 OK { message, cooldown_seconds: 60 }

    User->>Frontend: Enter 6-digit OTP Code
    Frontend->>API: POST /password/verify { email, code }
    API->>OTP: verify_otp(email, purpose, code)
    OTP->>OTP: Verify hash & attempt_count (< 5)
    OTP->>OTP: Generate cryptographically secure Reset Token
    OTP->>DB: Save token_hash, mark verified_at = now
    API-->>Frontend: 200 OK { reset_token, message }

    User->>Frontend: Enter New Password
    Frontend->>API: POST /password/reset { email, reset_token, new_password }
    API->>OTP: verify_reset_token(email, reset_token)
    API->>API: validate_password_policy(new_password)
    API->>API: check_password_history(user, new_password)
    API->>DB: Record old password hash in password_history
    API->>DB: Update user.password_hash
    API->>DB: Revoke all Refresh Tokens (all devices)
    API->>Mail: send_mail(to=email, template="password_changed")
    API-->>Frontend: 200 OK { message }
```

---

## Verification Token Controls (Part 16)
- Reset tokens are 32-byte cryptographically secure URL-safe tokens generated only upon successful 6-digit OTP verification.
- Only the SHA-256 hash of the reset token is stored in `verification_codes.token_hash`.
- Reset tokens are valid for 10 minutes, single-use only, and automatically revoked (`revoked_at = now`) after password reset completes.
