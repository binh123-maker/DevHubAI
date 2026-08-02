# DevHub AI - Actionable Phase 2 Implementation Roadmap

## Step-by-Step Execution Blueprint for Google & GitHub OAuth

### Step 1: Database Migration (Phase 2 Start)
Execute Alembic migration `006_create_oauth_accounts.py` to create `oauth_accounts` table in PostgreSQL.

### Step 2: Implement OAuth Provider Strategies
Concrete classes in `backend/app/auth/oauth/providers.py`:
- `GoogleProvider(IOAuthProvider)`: Uses `httpx` to exchange code at `https://oauth2.googleapis.com/token` and fetch user info from `https://www.googleapis.com/oauth2/v3/userinfo`.
- `GitHubProvider(IOAuthProvider)`: Uses `httpx` to exchange code at `https://github.com/login/oauth/access_token` and fetch user info from `https://api.github.com/user` & `https://api.github.com/user/emails`.

### Step 3: Register Endpoints in Auth Router
Add endpoints in `backend/app/api/v1/auth.py`:
- `GET /api/v1/auth/oauth/{provider}/url`: Returns authorization URL for Google/GitHub.
- `POST /api/v1/auth/oauth/{provider}/callback`: Accepts code, exchanges tokens, maps user account, and returns DevHub JWT token pair.

### Step 4: Frontend OAuth Buttons Integration
Connect Google & GitHub sign-in buttons in `LoginPage.tsx` and `RegisterPage.tsx` to initiate OAuth flow redirect.
