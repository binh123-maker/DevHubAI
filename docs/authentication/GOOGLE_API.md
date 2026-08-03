# DevHub AI - Google OAuth API Specification

## Endpoints Summary

### 1. `GET /api/v1/auth/oauth/google/login`
- **Description**: Generates Google OAuth authorization redirect URL and CSRF state token.
- **Query Parameters**: `redirect_uri` (e.g. `http://localhost:5173/auth/callback/google`)
- **Response**: `OAuthLoginUrlResponse` (`url`, `state`, `provider`)

### 2. `GET /api/v1/auth/oauth/google/callback`
- **Description**: Processes Google authorization code callback, validates identity claims, links user account, and issues DevHub JWT token pair.
- **Query Parameters**: `code`, `redirect_uri`
- **Response**: `TokenResponse` (`access_token`, `refresh_token`, `token_type`)

### 3. `GET /api/v1/auth/oauth/providers`
- **Description**: Provider discovery endpoint returning active provider health and metadata (Part 24).

### 4. `GET /api/v1/auth/oauth/accounts` & `DELETE /api/v1/auth/oauth/accounts/{id}`
- **Description**: Lists or unlinks connected OAuth accounts for current authenticated user.
