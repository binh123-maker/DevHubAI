# DevHub AI - Phase 3 API Contracts

## Overview
This document specifies the REST API endpoints introduced for Password Recovery and Password Management in Phase 3.

---

## Endpoint Specifications

### 1. `POST /api/v1/auth/password/forgot`
- **Request:**
  ```json
  { "email": "user@example.com" }
  ```
- **Response (200 OK):**
  ```json
  {
    "message": "Mã xác thực đã được gửi đến email của bạn.",
    "cooldown_seconds": 60
  }
  ```

---

### 2. `POST /api/v1/auth/password/verify`
- **Request:**
  ```json
  { "email": "user@example.com", "code": "123456" }
  ```
- **Response (200 OK):**
  ```json
  {
    "reset_token": "a1b2c3d4e5f6...",
    "message": "Mã OTP xác thực thành công."
  }
  ```

---

### 3. `POST /api/v1/auth/password/reset`
- **Request:**
  ```json
  {
    "email": "user@example.com",
    "reset_token": "a1b2c3d4e5f6...",
    "new_password": "NewPassword#2026",
    "new_password_confirm": "NewPassword#2026"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "message": "Đặt lại mật khẩu thành công. Vui lòng đăng nhập lại bằng mật khẩu mới."
  }
  ```

---

### 4. `POST /api/v1/auth/password/change` (Authenticated)
- **Headers:** `Authorization: Bearer <access_token>`
- **Request:**
  ```json
  {
    "current_password": "CurrentPassword#2026",
    "new_password": "NewPassword#2026",
    "new_password_confirm": "NewPassword#2026"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "message": "Đổi mật khẩu thành công."
  }
  ```
