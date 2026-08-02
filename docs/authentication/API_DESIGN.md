# DevHub AI - API Specification & REST Design Standards

## API Endpoint Blueprint

### Current Endpoints (`/api/v1/auth`)

| Endpoint | Method | Status | Request Body | Response Body | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/api/v1/auth/register` | `POST` | 201 | `RegisterRequest` | `TokenResponse` | Registers a new user and returns JWT token pair. |
| `/api/v1/auth/login` | `POST` | 200 | `LoginRequest` | `TokenResponse` | Authenticates user credentials and issues token pair. |
| `/api/v1/auth/refresh` | `POST` | 200 | `RefreshTokenRequest` | `TokenResponse` | Rotates refresh token and issues new access token. |
| `/api/v1/auth/logout` | `POST` | 200 | `LogoutRequest` | `{"message": "..."}` | Revokes the active refresh token. |
| `/api/v1/auth/me` | `GET` | 200 | *None* | `UserProfileResponse` | Fetches current user profile. |

---

### Future Phase 2+ Planned Endpoints

```yaml
# OAuth Endpoints
POST /api/v1/auth/oauth/{provider}/login:
  summary: Initiate OAuth login flow (google, github, etc.)
GET /api/v1/auth/oauth/{provider}/callback:
  summary: Process OAuth authorization code callback

# Email Verification & OTP Endpoints
POST /api/v1/auth/otp/send:
  summary: Request OTP dispatch (register, password_reset)
POST /api/v1/auth/otp/verify:
  summary: Validate OTP code

# Password Management
POST /api/v1/auth/password/forgot:
  summary: Initiate forgot password flow
POST /api/v1/auth/password/reset:
  summary: Execute password reset with verification code

# Session & Device Management
GET /api/v1/auth/sessions:
  summary: List active login sessions for user
DELETE /api/v1/auth/sessions/{session_id}:
  summary: Terminate a specific session
DELETE /api/v1/auth/sessions:
  summary: Terminate all other user sessions
```

## Standard Error Response Contract

All authentication errors conform to RFC 7807 problem details:

```json
{
  "status_code": 401,
  "detail": "Invalid credentials or token expired",
  "error_code": "AUTH_INVALID_CREDENTIALS",
  "timestamp": "2026-07-30T16:30:00Z"
}
```
