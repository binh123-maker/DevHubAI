# DevHub AI - Official Token & JWT Security Policy

## Policy Standards & Requirements

### 1. Access Token Specifications
- **Algorithm**: `HS256` HMAC-SHA256.
- **Lifetime**: 1440 minutes (24 hours).
- **Claims**: `sub` (User UUID), `exp` (Expiration UTC), `type` ("access").

### 2. Refresh Token Specifications
- **Format**: Cryptographically secure 48-byte random token (`secrets.token_urlsafe(48)`).
- **Storage Hashing**: Only SHA-256 token hashes are stored in the database (`token_hash`).
- **Lifetime**: 7 days.
- **Rotation**: On every `/auth/refresh` request, the presented refresh token is immediately revoked (`revoked_at = NOW()`) and a new refresh token is issued.

### 3. Token Reuse Protection
- If a revoked refresh token is presented to `/auth/refresh`, the system detects a token reuse attack and revokes all active refresh tokens for the affected user.
