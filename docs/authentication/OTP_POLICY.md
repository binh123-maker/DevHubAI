# DevHub AI - Official OTP Security Policy

## Policy Standards & Requirements

### 1. Code Generation & Format
- **Format**: 6-digit numeric string generated using cryptographic randomness (`secrets.choice`).
- **TTL**: 10 minutes from generation time.

### 2. Resend Cooldown & Attempt Limits
- **Cooldown**: Minimum 60-second wait between resend requests to prevent spam.
- **Attempt Limit**: Maximum 5 failed attempts per OTP code. Reaching 5 failures revokes the code.

### 3. Consumption Policy
- **One-Time Usage**: Once verified, the OTP is marked `consumed_at = NOW()` and cannot be reused.
