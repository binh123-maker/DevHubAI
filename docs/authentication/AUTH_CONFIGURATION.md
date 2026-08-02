# DevHub AI - Authentication Configuration Center Reference

## Overview

All authentication configuration parameters are centralized in `backend/app/auth/config.py` (`AuthConfig`). No authentication logic contains hardcoded numbers or magic strings.

---

## Configuration Item Catalog & Categorization

| Configuration Key | Data Type | Default Value | Categorization | Description |
| :--- | :--- | :--- | :--- | :--- |
| `access_token_expire_minutes` | `int` | `1440` (24h) | **SECURITY_CRITICAL** | Lifetime of encoded JWT access tokens. |
| `refresh_token_expire_days` | `int` | `7` | **SECURITY_CRITICAL** | Expiration period for refresh tokens. |
| `otp_expire_minutes` | `int` | `10` | **SECURITY_CRITICAL** | TTL for OTP verification codes. |
| `otp_length` | `int` | `6` | **PRODUCTION** | Number of digits in numeric OTP codes. |
| `max_otp_attempts` | `int` | `5` | **SECURITY_CRITICAL** | Failed OTP attempts before lockout. |
| `otp_cooldown_seconds` | `int` | `60` | **PRODUCTION** | Minimum interval between OTP resends. |
| `min_password_length` | `int` | `8` | **SECURITY_CRITICAL** | Minimum length for user passwords. |
| `max_password_length` | `int` | `128` | **PRODUCTION** | Maximum allowed password length. |
| `require_uppercase` | `bool` | `True` | **SECURITY_CRITICAL** | Require at least 1 uppercase letter. |
| `require_digit` | `bool` | `True` | **SECURITY_CRITICAL** | Require at least 1 numeric digit. |
| `require_special_char` | `bool` | `True` | **SECURITY_CRITICAL** | Require at least 1 special character. |
| `max_login_attempts` | `int` | `5` | **SECURITY_CRITICAL** | Account lock threshold for failed logins. |
| `session_idle_timeout_days` | `int` | `30` | **PRODUCTION** | Idle device session expiration. |
| `remember_me_expire_days` | `int` | `30` | **OPTIONAL** | Remember me persistent token duration. |
| `rate_limit_login_per_minute` | `int` | `10` | **SECURITY_CRITICAL** | Max login attempts per minute per IP. |
| `rate_limit_register_per_hour`| `int` | `5` | **SECURITY_CRITICAL** | Max register attempts per hour per IP. |
| `cookie_secure` | `bool` | `False` (`True` in Prod)| **PRODUCTION** | Require HTTPS for auth cookies. |
| `cookie_httponly` | `bool` | `True` | **SECURITY_CRITICAL** | Prevent client JavaScript token access. |
| `cookie_samesite` | `str` | `"lax"` | **SECURITY_CRITICAL** | CSRF protection cookie policy. |
