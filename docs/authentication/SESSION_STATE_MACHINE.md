# DevHub AI - Formal Session State Machine Specification

## State Diagram

```mermaid
stateDiagram-v2
    [*] --> CREATED: User Authenticated
    CREATED --> ACTIVE: Session Issued & Handshake Verified
    ACTIVE --> ACTIVE: Heartbeat / Refresh Token Rotated
    ACTIVE --> EXPIRED: Idle Timeout Exceeded (30 days)
    ACTIVE --> REVOKED: Security Alert / Password Changed / Admin Action
    ACTIVE --> LOGGED_OUT: Explicit User Logout
    EXPIRED --> [*]
    REVOKED --> [*]
    LOGGED_OUT --> [*]
```

## State Rules & Transitions
- **`CREATED`**: Session record instantiated in `login_sessions` table.
- **`ACTIVE`**: Active session with non-expired token pair.
- **`EXPIRED`**: Inactivated automatically when `expires_at < NOW()`.
- **`REVOKED`**: Terminated remotely or via security policy invalidation.
- **`LOGGED_OUT`**: User explicitly triggered logout.
