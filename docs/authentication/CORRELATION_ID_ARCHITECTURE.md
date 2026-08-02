# DevHub AI - Request Correlation ID Architecture

## Overview

The Request Correlation Architecture guarantees end-to-end traceability of authentication requests across HTTP API endpoints, security audit events, background jobs, mail dispatches, and log aggregators.

---

## Correlation ID Flow & Tracing

```
┌──────────────┐     X-Request-ID Header     ┌──────────────────┐
│ Client HTTP  ├────────────────────────────>│ FastAPI Middleware│
└──────────────┘                             └────────┬─────────┘
                                                      │ Inject Correlation ID
                                                      ▼
 ┌─────────────────┬──────────────────┬─────────────────┬──────────────────┐
 │ API Response    │ Security Events  │ Mail Service    │ OTP Engine       │
 │ (request_id)    │ (metadata)       │ (header)        │ (audit log)      │
 └─────────────────┴──────────────────┴─────────────────┴──────────────────┘
```

## Generation & Propagation Standard
1. **Header Name**: `X-Request-ID`.
2. **Format**: `req-<uuid4_short>` (e.g. `req-98f2a41b`).
3. **Behavior**: If incoming client request provides `X-Request-ID`, it is preserved. Otherwise, FastAPI middleware generates a fresh correlation ID.
4. **Logging Propagation**: Correlation ID is attached to structured log context and returned in all standard API response envelopes (`StandardAuthResponse.request_id`).
