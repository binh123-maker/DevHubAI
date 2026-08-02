# DevHub AI - Account State Machine Specification

## Account Lifecycle States & Transitions

```
[Pending Verification] ──(Verify Email)──> [Verified] ──(Activate Profile)──> [Active]
          │                                                                      │
          └───────────(Cancel/Timeout)──> [Deleted] <───(Admin/User Action)──────┴───┐
                                                                                     │
                                           [Locked] <──(Brute Force / Security Alert)┤
                                              │                                      │
                                       (Admin Unlock)                           (Admin Action)
                                              ▼                                      ▼
                                           [Active]                             [Suspended]
```

## State Definitions
- **`PENDING_VERIFICATION`**: User registered but email address not yet verified via OTP.
- **`VERIFIED`**: Email confirmed, preparing workspace default settings.
- **`ACTIVE`**: Fully active user in good standing.
- **`LOCKED`**: Temporarily restricted due to security policy or failed login threshold.
- **`SUSPENDED`**: Indefinitely disabled by system administrator.
- **`DELETED`**: Soft-deleted or permanently purged account.
