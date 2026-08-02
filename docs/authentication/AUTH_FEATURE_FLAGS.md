# DevHub AI - Authentication Feature Flags Architecture

## Overview

The Feature Flag system (`backend/app/auth/feature_flags.py`) enables software teams to toggle authentication features on or off safely across environments without modifying business logic.

---

## Feature Flag Catalog & Default Values

| Feature Flag Key | Default | Dependencies | Rollout Strategy | Description |
| :--- | :--- | :--- | :--- | :--- |
| `enable_email_login` | `True` | Baseline | Active | Standard Email & Password authentication. |
| `enable_google_login` | `True` | Phase 2 | Phase 2 Release | Google OAuth 2.0 authentication. |
| `enable_github_login` | `True` | Phase 2 | Phase 2 Release | GitHub OAuth 2.0 authentication. |
| `enable_microsoft_login` | `False` | Phase 2+ | Future | Microsoft OAuth 2.0 authentication. |
| `enable_otp` | `True` | Phase 3 | Phase 3 Release | One-Time Passcode verification engine. |
| `enable_remember_me` | `True` | Phase 3 | Active | Persistent Remember Me login session token. |
| `enable_captcha` | `False` | External API | Opt-in | CAPTCHA protection on public endpoints. |
| `enable_account_linking` | `True` | Phase 2 | Phase 2 Release | Multi-provider account linking. |
| `enable_login_history` | `True` | Phase 4 | Phase 4 Release | User login security audit event trail. |
| `enable_device_sessions` | `True` | Phase 3 | Phase 3 Release | Active device session tracking & revocation. |
| `enable_two_factor` | `False` | Phase 4 | Future | Two-Factor Authentication (2FA). |
