# DevHub AI - Architectural Decision Record (ADR): Google-Only Authentication Architecture

## Status
**ACCEPTED / APPROVED** (Phase 2.5 Architecture Refinement)

---

## Context & Background

DevHub AI's authentication subsystem was originally designed with a multi-provider dynamic OAuth plugin registry structure. Following a strategic product roadmap update, DevHub AI officially standardizes on **Google OAuth** as its sole external identity provider. GitHub OAuth and other planned social identity providers are permanently removed from the active roadmap.

This Architectural Decision Record documents the technical rationale, database schema design, boundary trade-offs, security policies, and future extensibility strategies governing the single-provider Google Identity integration.

---

## Decisions

### 1. Removal of GitHub OAuth & Multi-Provider Dynamic Registry
- **Decision:** Remove GitHub OAuth handlers, endpoints, icons, dynamic provider priorities, and dynamic lookup logic.
- **Rationale:** Standardizing on Google simplifies the runtime path, reduces dependency surface area, eliminates unnecessary complexity, and optimizes maintenance overhead.

### 2. Preservation of Generic Database Schema (`provider_user_id` and `provider`)
- **Decision:** Keep the column name `provider_user_id` (storing Google's `sub` claim) instead of renaming it to `google_sub`. Retain the `provider` column with a default value of `'google'` and a `CHECK (provider = 'google')` constraint.
- **Rationale:** Preserving provider-neutral field names prevents expensive database migrations in the future if product requirements ever re-introduce another identity provider, ensuring zero-redesign database architecture.

### 3. Simplified Single-Provider Abstractions (`IOAuthProvider` & `GoogleProvider`)
- **Decision:** Maintain `IOAuthProvider` abstract base interface and `GoogleProvider` implementation, while deprecating dynamic lookup registries.
- **Rationale:** Retaining clean domain interfaces maintains OOP strategy boundaries and testability while stripping away unnecessary dynamic dynamic registration boilerplate.

### 4. Grouped OAuth Namespace API Routes
- **Decision:** All Google OAuth endpoints remain strictly under the `/api/v1/auth/oauth/google/` namespace:
  - `GET /api/v1/auth/oauth/google/login`
  - `GET /api/v1/auth/oauth/google/callback`
  - `GET /api/v1/auth/oauth/google/status`
  - `POST /api/v1/auth/oauth/google/disconnect`
- **Rationale:** Maintains consistent API path hierarchy and prevents breaking client contract patterns.

### 5. Safe Google Disconnect Policy
- **Decision:** Disconnecting a Google account requires the user to have an active local password (`user.password_hash`). If no local password exists, the API rejects the disconnect request (HTTP 400) and prompts the user to set a password first.
- **Rationale:** Prevents account lockout and orphaned identity scenarios where users could accidentally lose access to their account.

### 6. Rich Provider Metadata Retention (`provider_metadata`)
- **Decision:** Retain `provider_metadata` as a PostgreSQL `JSONB` column to store normalized Google claims (`locale`, `picture`, `given_name`, `family_name`, `hosted_domain`, `email_verified`, `raw_claims`).
- **Rationale:** Enables non-destructive user profile synchronization and future audit tracking without altering tabular schema.

---

## Simplified `OAuthAccount` Schema

```sql
CREATE TABLE oauth_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL DEFAULT 'google',
    provider_user_id VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    avatar_url VARCHAR(500),
    provider_metadata JSONB,
    linked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_oauth_provider_user_id UNIQUE (provider, provider_user_id),
    CONSTRAINT uq_oauth_user_id_provider UNIQUE (user_id, provider),
    CONSTRAINT ck_oauth_accounts_provider_google CHECK (provider = 'google')
);

CREATE INDEX ix_oauth_accounts_user_id ON oauth_accounts (user_id);
CREATE INDEX ix_oauth_accounts_email ON oauth_accounts (email);
```

---

## Security Considerations

1. **Mandatory Email Verification:** Only Google accounts with `email_verified == true` are allowed to authenticate or link.
2. **CSRF Protection:** State parameter validation (`oauth_state`) is strictly enforced on authorization callbacks.
3. **Identity-Only Policy:** OAuth access tokens exchanged with Google are used strictly in-memory during authentication and are discarded immediately afterward.
4. **Safe Disconnect Enforcement:** Disconnect endpoint guarantees that users maintain at least one valid authentication method.

---

## Trade-off Analysis

| Metric | Before Refactor (Multi-Provider) | After Refactor (Google-Only) |
| :--- | :--- | :--- |
| **Provider Complexity** | High (Registry, Priority, Selection) | Minimal (Direct GoogleProvider) |
| **Database Schema** | 16 fields in `oauth_accounts` | 12 fields (Clean & minimal) |
| **API Endpoints** | Dynamic `/oauth/{provider}/*` | Standardized `/oauth/google/*` |
| **Extensibility** | Built for 5+ social providers | Neutral schema ready for future expansion without migration |
