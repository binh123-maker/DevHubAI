# DevHub AI - Google OAuth UI & Frontend Flow

## Frontend Components & User Flows

1. **Login & Register Buttons**:
   - `LoginPage.tsx` and `RegisterPage.tsx` render "Continue with Google" buttons matching Google branding guidelines.
   - Clicking triggers `authApi.getOAuthUrl("google", redirectUri)`.
2. **Callback Handler (`OAuthCallbackPage.tsx`)**:
   - Listens on `/auth/callback/google`.
   - Validates CSRF `state` from `sessionStorage`.
   - Sends `code` to backend callback endpoint `/api/v1/auth/oauth/google/callback`.
   - Stores `access_token` and `refresh_token` via `tokenStorage`.
   - Navigates user to `/workspaces`.
3. **Linked Accounts UI (`SettingsPage.tsx`)**:
   - Displays connected Google provider badge, email, linked date, and "Disconnect" button.
