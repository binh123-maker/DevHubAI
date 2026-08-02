# DevHub AI - Transactional Mail Template Architecture

## Overview

The Mail Template System abstracts email delivery provider implementation (SMTP, SendGrid, AWS SES) and manages HTML/plain-text email templates with variable substitution and localization.

## Template Specifications Matrix

| Template Type | Subject Line Template | Variables | Description |
| :--- | :--- | :--- | :--- |
| `WELCOME` | "Welcome to DevHub AI, {full_name}!" | `full_name` | Sent upon new account creation. |
| `EMAIL_VERIFICATION_OTP` | "Your DevHub AI Verification Code: {otp_code}" | `otp_code`, `ttl_minutes` | OTP code for email verification. |
| `PASSWORD_RESET_OTP` | "Reset your DevHub AI Password" | `otp_code`, `ttl_minutes` | OTP code for password reset. |
| `ACCOUNT_LOCKED` | "Security Alert: Account Temporarily Locked" | `full_name`, `support_url` | Sent after excessive failed logins. |
