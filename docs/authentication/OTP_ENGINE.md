# DevHub AI - OTP Verification Engine Specification (Phase 3)

## Overview
The `OTPService` is an enterprise-grade One-Time Passcode engine responsible for generation, hashing, rate limiting, cooldown tracking, and verification code lifecycle management.

---

## Technical Security Parameters (Parts 9 & 24)

| Parameter | Configuration Value | Environment Variable | Rationale / Mitigation |
| :--- | :--- | :--- | :--- |
| **Code Format** | 6-Digit Numeric (`000000`-`999999`) | `OTP_LENGTH=6` | Secure & mobile-friendly entry |
| **Lifetime (TTL)** | 10 Minutes | `OTP_EXPIRE_MINUTES=10` | Minimizes exposure window |
| **Max Failed Attempts** | 5 Attempts | `OTP_MAX_ATTEMPTS=5` | Prevents brute-force guessing |
| **Resend Cooldown** | 60 Seconds | `OTP_RESEND_COOLDOWN=60` | Prevents mail spam |
| **Rate Limit / Email** | Max 5 OTP / Hour | N/A | Prevents abuse targeting specific accounts |
| **Storage Mechanic** | Salted SHA-256 Hash | N/A | Never stores plain text codes in DB |

---

## Automatic Code Cleanup (Part 17)
The `OTPService.cleanup_expired_codes(db)` background task periodically deletes records where `expires_at < now` or `revoked_at IS NOT NULL`. It supports execution via Cron, APScheduler, or Celery Beat without altering business logic.
