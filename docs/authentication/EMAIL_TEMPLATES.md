# DevHub AI - Email Templates Specification (Part 23)

## Overview
Phase 3 includes responsive HTML and plain text templates for transactional emails, designed for dark mode, mobile devices, and major mail clients (Gmail, Outlook, Apple Mail).

---

## Template Specifications

### 1. `forgot_password` (OTP Verification)
- **Subject:** `Mã xác thực khôi phục mật khẩu DevHub AI`
- **Variables:** `{full_name}`, `{otp_code}`, `{ttl_minutes}`
- **Design:** Centered dark-themed card (`#1e293b`), styled 6-digit OTP container (`#38bdf8`), expiry notice.

### 2. `password_changed` (Security Alert)
- **Subject:** `Thông báo bảo mật: Mật khẩu DevHub AI đã được thay đổi`
- **Variables:** `{full_name}`
- **Design:** Green security alert badge (`#10b981`), advice regarding session revocation across all devices.
