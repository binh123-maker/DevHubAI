# DevHub AI - Formal OAuth State Machine Specification

## State Diagram

```mermaid
stateDiagram-v2
    [*] --> REDIRECT: User initiates OAuth login
    REDIRECT --> AUTHORIZATION: Redirect to Provider Auth Page
    AUTHORIZATION --> CALLBACK: User authorizes & callback received
    CALLBACK --> TOKEN_EXCHANGE: Exchange code for provider access_token
    TOKEN_EXCHANGE --> IDENTITY_VERIFICATION: Fetch provider user claims & email
    IDENTITY_VERIFICATION --> ACCOUNT_LINKING: Match/Link local User profile
    ACCOUNT_LINKING --> COMPLETED: DevHub JWT Token Pair Issued
    TOKEN_EXCHANGE --> FAILED: Invalid Code / Provider Error
    IDENTITY_VERIFICATION --> FAILED: Email Unverified
    ACCOUNT_LINKING --> FAILED: Account Lock Conflict
    COMPLETED --> [*]
    FAILED --> [*]
```

## State Rules
- **`REDIRECT`**: Generate PKCE / CSRF state token and compute authorization URL.
- **`AUTHORIZATION`**: External authorization prompt rendered by OAuth provider.
- **`CALLBACK`**: Validate CSRF state token and parse authorization code.
- **`TOKEN_EXCHANGE`**: Server-to-server token endpoint request.
- **`IDENTITY_VERIFICATION`**: Normalize provider identity schema (`OAuthUserInfo`).
- **`ACCOUNT_LINKING`**: Link to existing user via email or instantiate new user record.
- **`COMPLETED`**: Issue standard JWT token pair.
