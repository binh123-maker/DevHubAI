# DevHub AI - Google OAuth Testing Strategy

## Test Plan Overview

All Google OAuth features are tested via `backend/tests/test_oauth.py` using `httpx` HTTP mock interceptors.

## Test Scenarios Covered
1. **New User Registration via Google OAuth**: Verify creation of `User`, `UserProfile`, `Workspace`, and `OAuthAccount`.
2. **Account Linking**: Verify linking Google account to existing user with matching verified email.
3. **Existing Linked User Login**: Verify timestamp updates and token pair issuance.
4. **Unverified Email Rejection**: Verify HTTP 400 rejection when `email_verified == False`.
5. **Code Exchange Failure**: Verify HTTP 502 handling when Google token endpoint fails.
6. **Unlinking Account**: Verify unlinking OAuth account and blocking unlinking of sole auth method.
