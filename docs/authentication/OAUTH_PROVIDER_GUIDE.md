# DevHub AI - Developer Guide: Adding GitHub OAuth in Phase 3

## Overview & Phase 3 Compatibility Certification

Phase 2 certifies that future OAuth providers (GitHub, Microsoft, GitLab) can be added **WITHOUT ANY ARCHITECTURAL REDESIGN** or modifications to the core database schema (`oauth_accounts`), token manager, or response standard envelopes.

---

## Step-by-Step Developer Guide for Phase 3 (GitHub OAuth)

To implement GitHub OAuth in Phase 3, developers only need to perform 4 localized steps:

### 1. Create `GitHubProvider` (`backend/app/auth/oauth/github.py`)
Implement `IOAuthProvider` interface for GitHub:
- `provider_name`: returns `"github"`.
- `get_authorization_url(state, redirect_uri)`: computes `https://github.com/login/oauth/authorize`.
- `exchange_code_for_token(code, redirect_uri)`: exchanges code at `https://github.com/login/oauth/access_token`.
- `fetch_user_info(access_token)`: fetches profile from `https://api.github.com/user` & `https://api.github.com/user/emails`.
- Auto-register plugin with `plugin_registry.register_plugin(...)`.

### 2. Add Settings Configuration (`backend/app/core/config.py`)
Add `github_client_id: str = ""` and `github_client_secret: str = ""`.

### 3. Add GitHub Button to Frontend (`LoginPage.tsx` & `RegisterPage.tsx`)
Connect the existing GitHub button to call `authApi.getOAuthUrl("github", redirectUri)`.

### 4. Zero Schema / Zero Architecture Modifications Needed!
`oauth_accounts` table, `OAuthAccountService`, `TokenManager`, `OAuthCallbackPage.tsx`, and `SettingsPage.tsx` already support GitHub automatically via the unified `provider` discriminator column!
