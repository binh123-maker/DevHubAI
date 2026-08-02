# DevHub AI - Strongly Typed Authentication Constants

## Overview

All authentication constants are strictly typed Python `Enum` definitions (`backend/app/auth/constants/enums.py`). Raw string literals ("magic strings") are prohibited in business logic code.

---

## Enumeration Definitions

### 1. `AuthProvider`
- `LOCAL = "local"`
- `EMAIL = "email"`
- `GOOGLE = "google"`
- `GITHUB = "github"`
- `MICROSOFT = "microsoft"`
- `GITLAB = "gitlab"`
- `FACEBOOK = "facebook"`
- `LINKEDIN = "linkedin"`

### 2. `TokenType`
- `ACCESS = "access"`
- `REFRESH = "refresh"`
- `VERIFICATION = "verification"`
- `RESET = "reset"`

### 3. `OTPPurpose`
- `REGISTER = "register"`
- `PASSWORD_RESET = "password_reset"`
- `EMAIL_CHANGE = "email_change"`
- `ACCOUNT_DELETE = "account_delete"`
- `TWO_FACTOR = "two_factor"`

### 4. `SessionStatus`
- `CREATED = "created"`
- `ACTIVE = "active"`
- `EXPIRED = "expired"`
- `REVOKED = "revoked"`
- `LOGGED_OUT = "logged_out"`

### 5. `UserState`
- `PENDING_VERIFICATION = "pending_verification"`
- `VERIFIED = "verified"`
- `ACTIVE = "active"`
- `LOCKED = "locked"`
- `SUSPENDED = "suspended"`
- `DELETED = "deleted"`
