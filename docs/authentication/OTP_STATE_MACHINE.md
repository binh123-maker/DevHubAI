# DevHub AI - Formal OTP State Machine Specification

## State Diagram

```mermaid
stateDiagram-v2
    [*] --> GENERATED: Issue Code Request
    GENERATED --> SENT: Dispatched via Provider
    SENT --> VERIFIED: Valid Code Input (Attempts < 5 & TTL < 10m)
    SENT --> ATTEMPT_FAILED: Invalid Code Input
    ATTEMPT_FAILED --> SENT: Retry (Attempts < 5)
    ATTEMPT_FAILED --> REVOKED: Max Attempts Exceeded (5)
    SENT --> EXPIRED: TTL Exceeded (> 10 min)
    VERIFIED --> USED: Consumed by Scenario
    USED --> [*]
    REVOKED --> [*]
    EXPIRED --> [*]
```

## State Definitions & Recovery Rules
- **`GENERATED`**: Secure OTP code string created in memory/DB.
- **`SENT`**: Code successfully dispatched to email/SMS target.
- **`VERIFIED`**: OTP matched; state transitions to single-use consumption.
- **`USED`**: Terminal state preventing replay attacks.
- **`EXPIRED`**: Code automatically invalidated after 10-minute TTL.
- **`REVOKED`**: Locked out due to 5 consecutive failed attempts. User must wait 60s cooldown before requesting a new code.
