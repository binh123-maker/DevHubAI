# DevHub AI - Google OAuth 2.0 Integration Architecture

## Overview & Identity-Only Policy

DevHub AI implements Google OAuth 2.0 strictly for **Authentication and Identity Verification**. The system operates under a strict **Identity-Only OAuth Policy** (Part 17):
- Google access tokens and refresh tokens are processed in-memory during the callback handshake ONLY to retrieve identity claims (`sub`, `email`, `name`, `picture`).
- Provider access tokens are **NEVER stored permanently in the database**.
- The `oauth_accounts` table stores ONLY identity metadata (`provider`, `provider_user_id`, `email`, `display_name`, `avatar_url`, `linked_at`, `last_login_at`).

---

## Strategy Pattern Implementation

```
┌─────────────────────────────────────────────────────────┐
│                     IOAuthProvider                      │
│                  (Abstract Strategy)                    │
└────────────────────────────┬────────────────────────────┘
                             │ Implements
┌────────────────────────────▼────────────────────────────┐
│                     GoogleProvider                      │
│     (backend/app/auth/oauth/google.py)                 │
└────────────────────────────┬────────────────────────────┘
                             │ Registers
┌────────────────────────────▼────────────────────────────┐
│                  OAuthPluginRegistry                    │
│   (backend/app/auth/oauth/plugin_registry.py)          │
└─────────────────────────────────────────────────────────┘
```
