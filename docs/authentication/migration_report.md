# DevHub AI - Database Migration Report (Phase 2.5 Google OAuth Refactoring)

## Overview
This report details the Alembic database migration (`007_refactor_oauth_google_only.py`) generated for simplifying the `oauth_accounts` table schema to support Google-only authentication while maintaining provider-neutral schema compatibility.

---

## Migration Details
- **Migration ID:** `007_refactor_oauth_google_only`
- **Revises:** `006_oauth_accounts`
- **Script Location:** `backend/alembic/versions/007_refactor_oauth_google_only.py`

---

## DDL Operations Summary

| Target Table | Action | Column / Constraint | Rationale / ADR Reference |
| :--- | :--- | :--- | :--- |
| `oauth_accounts` | DROP COLUMN | `is_primary_provider` | Unnecessary field (ADR 7) |
| `oauth_accounts` | DROP COLUMN | `provider_status` | Unnecessary field (ADR 7) |
| `oauth_accounts` | DROP COLUMN | `last_sync_at` | Activity tracked via `last_login_at` & `updated_at` (ADR 7) |
| `oauth_accounts` | DROP COLUMN | `provider_version` | Unnecessary field (ADR 7) |
| `oauth_accounts` | ADD CHECK | `ck_oauth_accounts_provider_google` | Enforces `provider = 'google'` (ADR 2) |
| `oauth_accounts` | ADD INDEX | `ix_oauth_accounts_email` | Fast lookup by email address (ADR 1 & 7) |

---

## Preserved Columns & Constraints
- `provider`: Kept with default value `'google'` (ADR 2).
- `provider_user_id`: Kept storing Google's `sub` claim (ADR 1).
- `provider_metadata`: Kept as `JSONB` for storing Google claims (`locale`, `picture`, `email_verified`, `given_name`, `family_name`, `hosted_domain`, `raw_claims`) (ADR 6).
- `uq_oauth_provider_user_id`: Unique constraint on `(provider, provider_user_id)`.
- `uq_oauth_user_id_provider`: Unique constraint on `(user_id, provider)`.

---

## Rollback Verification (Downgrade)
The downgrade path recreates dropped columns with their original defaults (`is_primary_provider`, `provider_status`, `last_sync_at`, `provider_version`), drops `ix_oauth_accounts_email`, and drops `ck_oauth_accounts_provider_google`.
