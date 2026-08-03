# DevHub AI - Security Event Logging Specification (Phase 3)

## Overview
Phase 3 mandates comprehensive auditing of all authentication and password events.

---

## Audited Event Types (Part 20)

| Event Type | Description | Trigger |
| :--- | :--- | :--- |
| `PASSWORD_RESET_REQUEST` | User requested password recovery OTP | `POST /password/forgot` |
| `OTP_SENT` | OTP code dispatched via MailService | `POST /password/forgot` |
| `OTP_FAILED` | Incorrect or expired OTP submitted | `POST /password/verify` |
| `OTP_VERIFIED` | OTP code verified, reset token issued | `POST /password/verify` |
| `PASSWORD_RESET_SUCCESS` | Password reset completed via token | `POST /password/reset` |
| `PASSWORD_CHANGED` | Password changed by logged-in user | `POST /password/change` |
| `PASSWORD_CHANGE_FAILED` | Current password incorrect or policy error | `POST /password/change` |
| `PASSWORD_POLICY_VIOLATION` | Submitted password failed policy rules | Password validation failure |

---

## Log Record Payload Structure
Each event records: `user_id`, `email`, `ip_address`, `user_agent`, `timestamp`, `result`, `reason`.
