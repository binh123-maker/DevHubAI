# DevHub AI - Master Namespaced Error Code Catalog

## Overview

All authentication errors use namespaced error codes (`AUTH_<MODULE>_<NUMBER>`) defined in `backend/app/auth/errors/codes.py`. Every error specifies a unique code, HTTP status, developer message, user message, severity, and recoverability flag.

---

## Error Catalog Matrix

| Error Code | HTTP Status | User Message | Developer Message | Severity | Recoverable |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `AUTH_LOGIN_001` | 401 | Invalid email or password. | Credentials check failed for given email. | WARNING | Yes |
| `AUTH_LOGIN_002` | 401 | Password incorrect. | Password verification failed against hash. | WARNING | Yes |
| `AUTH_LOGIN_003` | 423 | Account locked due to excessive failed attempts. | `max_login_attempts` threshold exceeded. | CRITICAL | No |
| `AUTH_LOGIN_004` | 403 | Account is inactive or suspended. | User `is_active` flag is False or State is Suspended. | CRITICAL | No |
| `AUTH_TOKEN_001` | 401 | Session expired. Please sign in again. | JWT access token expiration ('exp') exceeded. | INFO | Yes |
| `AUTH_TOKEN_002` | 401 | Invalid access token. | JWT signature or header decode failure. | WARNING | Yes |
| `AUTH_TOKEN_003` | 401 | Refresh token expired. | Database `refresh_tokens.expires_at < NOW()`. | INFO | Yes |
| `AUTH_TOKEN_004` | 401 | Refresh token revoked or reused. | Token revoked or reuse attempt detected. | CRITICAL | No |
| `AUTH_SESSION_001` | 401 | Session expired. | Idle session timeout exceeded. | INFO | Yes |
| `AUTH_SESSION_002` | 401 | Session terminated. | Session explicitly revoked by user or admin. | WARNING | Yes |
| `AUTH_OTP_001` | 400 | Verification code expired. | OTP code TTL (>10 min) exceeded. | WARNING | Yes |
| `AUTH_OTP_002` | 400 | Invalid verification code. | Entered OTP numeric string mismatch. | WARNING | Yes |
| `AUTH_OTP_003` | 429 | Too many failed OTP attempts. | `max_otp_attempts` threshold reached. | CRITICAL | No |
| `AUTH_OTP_004` | 429 | Please wait before requesting another code. | Resend cooldown active (<60s). | WARNING | Yes |
| `AUTH_PROVIDER_001` | 400 | Provider disabled. | Feature flag for provider is set to False. | WARNING | Yes |
| `AUTH_PROVIDER_002` | 502 | Provider communication failed. | Remote OAuth token exchange endpoint failed. | CRITICAL | Yes |
| `AUTH_ACCOUNT_001` | 409 | Email address already registered. | Database unique email constraint conflict. | WARNING | Yes |
| `AUTH_ACCOUNT_002` | 422 | Password complexity mismatch. | Password fails complexity criteria. | WARNING | Yes |
| `AUTH_ACCOUNT_003` | 401 | Authentication required. | Endpoint accessed without Bearer token. | INFO | Yes |
