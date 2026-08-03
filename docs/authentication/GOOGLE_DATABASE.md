# DevHub AI - Google OAuth Database Schema Specifications

## Table Definition (`oauth_accounts`)

```sql
CREATE TABLE oauth_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL, -- 'google', 'github', etc.
    provider_user_id VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    avatar_url VARCHAR(500),
    is_primary_provider BOOLEAN NOT NULL DEFAULT FALSE,
    provider_status VARCHAR(50) NOT NULL DEFAULT 'active',
    last_sync_at TIMESTAMPTZ,
    provider_version VARCHAR(20) NOT NULL DEFAULT 'v2',
    provider_metadata JSONB,
    linked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_oauth_provider_user_id UNIQUE (provider, provider_user_id),
    CONSTRAINT uq_oauth_user_id_provider UNIQUE (user_id, provider)
);

CREATE INDEX ix_oauth_accounts_user_id ON oauth_accounts(user_id);
CREATE INDEX ix_oauth_accounts_provider_user ON oauth_accounts(provider, provider_user_id);
```
