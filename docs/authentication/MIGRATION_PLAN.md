# DevHub AI - Database Migration Roadmap (Phase 2 - Phase 4)

## Alembic Migration Execution Strategy

```
Phase 1 (Current)           Phase 2 (OAuth)             Phase 3 (OTP & Sessions)     Phase 4 (Security & Audit)
┌───────────────────────┐   ┌───────────────────────┐   ┌───────────────────────┐    ┌───────────────────────┐
│ Schema Audit & DDL    │──>│ create_oauth_accounts │──>│ create_verification   │───>│ create_security_events│
│ Design (No Migrations)│   │ table                 │   │ _codes & sessions     │    │ & composite indexes   │
└───────────────────────┘   └───────────────────────┘   └───────────────────────┘    └───────────────────────┘
```

## Migration Scripts Order & Dependency Map

### Migration 1 (Phase 2): `006_create_oauth_accounts.py`
- Creates `oauth_accounts` table.
- Adds FK constraint `user_id` -> `users.id` ON DELETE CASCADE.
- Adds UNIQUE constraint `(provider, provider_user_id)`.
- **Rollback**: Drop `oauth_accounts` table.

### Migration 2 (Phase 3): `007_create_verification_and_sessions.py`
- Creates `verification_codes` table.
- Creates `login_sessions` table.
- **Rollback**: Drop `login_sessions` and `verification_codes` tables.

### Migration 3 (Phase 4): `008_create_security_events.py`
- Creates `security_events` table.
- Adds composite indexes `ix_refresh_tokens_expires_revoked` on `refresh_tokens(expires_at, revoked_at)`.
- **Rollback**: Drop composite indexes and `security_events` table.
