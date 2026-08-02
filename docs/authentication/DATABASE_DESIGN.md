# DevHub AI - Database Schema Review & Future DDL Design

## Current Database Model Review

The existing database schema includes 3 authentication-related tables: `users`, `user_profiles`, and `refresh_tokens`.

```sql
-- Existing Tables Summary
-- users: (id UUID, email VARCHAR, password_hash VARCHAR, oauth_provider ENUM, role ENUM, is_active BOOL)
-- user_profiles: (id UUID, user_id UUID FK, full_name VARCHAR, avatar_url VARCHAR, gender ENUM)
-- refresh_tokens: (id UUID, user_id UUID FK, token_hash VARCHAR UNIQUE, expires_at TIMESTAMPTZ, revoked_at TIMESTAMPTZ)
```

---

## Future Database Schema Design (Phase 2+)

```sql
-- 1. OAuth Accounts Table (Supports multi-provider linking)
CREATE TABLE oauth_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL, -- 'google', 'github', 'microsoft', etc.
    provider_user_id VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(500),
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_oauth_provider_user UNIQUE (provider, provider_user_id)
);
CREATE INDEX ix_oauth_accounts_user_id ON oauth_accounts(user_id);

-- 2. Email & OTP Verification Codes Table
CREATE TABLE verification_codes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    target VARCHAR(255) NOT NULL, -- Email address or phone number
    purpose VARCHAR(50) NOT NULL, -- 'register', 'password_reset', etc.
    code_hash VARCHAR(255) NOT NULL,
    attempts_count INT NOT NULL DEFAULT 0,
    max_attempts INT NOT NULL DEFAULT 5,
    expires_at TIMESTAMPTZ NOT NULL,
    consumed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_verification_codes_target_purpose ON verification_codes(target, purpose);

-- 3. Login Sessions & Device Tracking Table
CREATE TABLE login_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token_hash VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    device_name VARCHAR(100),
    location VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_active_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_login_sessions_user_active ON login_sessions(user_id, is_active);

-- 4. Security Events & Audit Trail Table
CREATE TABLE security_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL, -- 'login_success', 'password_changed', etc.
    severity VARCHAR(20) NOT NULL DEFAULT 'info', -- 'info', 'warning', 'critical'
    ip_address VARCHAR(45),
    user_agent TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_security_events_user_event ON security_events(user_id, event_type);
CREATE INDEX ix_security_events_created_at ON security_events(created_at DESC);
```
