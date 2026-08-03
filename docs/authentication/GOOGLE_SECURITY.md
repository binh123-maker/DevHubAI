# DevHub AI - Google OAuth Security Architecture & Controls

## Security Controls

1. **CSRF State Verification**:
   - Authorization URL injects cryptographically random state (`sessionStorage` verification on client side).
2. **Identity-Only Token Policy (Part 17)**:
   - Google access/refresh tokens are kept in transient RAM during code exchange and discarded immediately. No provider tokens stored in PostgreSQL.
3. **Mandatory Email Verification (Part 18)**:
   - Verification check enforces `email_verified == True`. Accounts with unverified emails are strictly rejected.
4. **Account Linking Lockout (Part 19)**:
   - 1:1 mapping enforced between Google sub and DevHub User. Unlinking is blocked if it would leave the user with zero remaining auth methods.
5. **DevHub-Isolated Logout (Part 22)**:
   - Logging out of DevHub terminates only the DevHub JWT session; it does NOT alter the user's Google session.
