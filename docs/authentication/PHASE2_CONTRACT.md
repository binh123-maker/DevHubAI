# DevHub AI - Strict Phase 2 Implementation Contract

## Scope & Permitted Actions for Phase 2 Developers

Phase 2 will implement Google OAuth and GitHub OAuth authentication.

### Permitted Modifications:
- Implementing concrete `GoogleProvider` and `GitHubProvider` classes implementing `IOAuthProvider`.
- Registering provider instances with `OAuthPluginRegistry`.
- Executing Alembic migration `006_create_oauth_accounts.py`.
- Implementing OAuth API endpoints (`/auth/oauth/google/login`, `/callback`, `/auth/oauth/github/login`, `/callback`).
- Wiring frontend Google & GitHub buttons to OAuth authorization endpoints.

### Prohibited Modifications:
- Modifying `backend/app/auth/` directory structure.
- Altering existing `AuthConfig` parameter definitions or `enums.py` values.
- Modifying `StandardAuthResponse` or `AuthErrorCode` structure.
- Redesigning existing `/login`, `/register`, `/refresh`, `/logout`, `/me` endpoints.
- Modifying `users`, `user_profiles`, or `refresh_tokens` base schemas.
