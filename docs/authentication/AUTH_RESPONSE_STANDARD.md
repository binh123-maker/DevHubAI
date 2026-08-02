# DevHub AI - Versioned API Response Specification

## Overview

All authentication endpoints conform to the `StandardAuthResponse[T]` envelope (`backend/app/auth/schemas/responses.py`). This standardizes response structures, supports API versioning, provides status codes, and injects request correlation IDs for end-to-end tracing.

---

## Response Envelope Structure

```json
{
  "version": "v1",
  "success": true,
  "code": "AUTH_SUCCESS",
  "message": "Authentication successful.",
  "data": {
    "access_token": "eyJhbGciOi...",
    "refresh_token": "d7a8f9...",
    "token_type": "bearer"
  },
  "timestamp": "2026-08-02T07:24:00Z",
  "request_id": "req-98f2a41b"
}
```

## Error Response Example

```json
{
  "version": "v1",
  "success": false,
  "code": "AUTH_LOGIN_001",
  "message": "Invalid email or password.",
  "data": null,
  "timestamp": "2026-08-02T07:24:00Z",
  "request_id": "req-98f2a41b"
}
```
