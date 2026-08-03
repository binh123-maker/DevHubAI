# DevHub AI - Pre-Production Security Checklist for Google OAuth

## Pre-Production Verification Checklist

- [x] **Identity-Only Policy**: Zero Google access or refresh tokens persisted in DB (`oauth_accounts`).
- [x] **Email Verification Enforcement**: Reject logins when `email_verified == False`.
- [x] **CSRF State Token Validation**: Random `state` string validated during handshake.
- [x] **Account Linking Isolation**: One-to-one mapping between Google `sub` and DevHub `user_id`.
- [x] **Sole Auth Method Unlink Protection**: Users blocked from disconnecting sole authentication method.
- [x] **DevHub-Isolated Logout**: DevHub logout invalidates only DevHub JWT/Refresh session.
- [x] **Non-Destructive Profile Sync**: Local profile customizations preserved on subsequent OAuth logins.
- [x] **100% Post-Registration Business Logic Reuse**: Registration reuses existing `User`, `UserProfile`, and `Workspace` services.
