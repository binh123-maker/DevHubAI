# DevHub AI - Authentication Architecture Blueprint

## System Overview

The DevHub AI Authentication Architecture follows a decoupled, modular domain model designed for high scalability, security isolation, and enterprise maintainability.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Frontend Presentation Layer                       │
│  (React 18 + React Router + AuthContext + TokenStorage Adapter + Axios)      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTPS / JSON REST API
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                            Backend API Routing Layer                        │
│                           (FastAPI Router @ /api/v1/auth)                   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                             Auth Domain Services Layer                      │
│                  (app/auth Domain Abstractions & Subservices)               │
├─────────────────┬──────────────────┬──────────────────┬─────────────────────┤
│  OAuth Strategy │  OTP Engine      │ Session Manager  │  Security Audit Log │
│  (IOAuthProvider)│ (IOTPService)   │(ISessionManager) │ (ISecurityLogger)   │
└─────────────────┴──────────────────┴──────────────────┴─────────────────────┤
                                       │ SQLAlchemy ORM
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                           Database Infrastructure Layer                     │
│                (PostgreSQL Database: users, refresh_tokens, etc.)           │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Core Module Boundaries

### 1. `backend/app/auth/`
- **`controllers/`**: API endpoint handlers parsing payloads and enforcing HTTP response standards.
- **`services/`**: Core authentication domain logic (registration, credential validation, token rotation).
- **`interfaces/`**: Abstract base classes defining explicit service contracts.
- **`security/`**: Cryptographic password hashing, JWT encoding/decoding, and random code generation.
- **`oauth/`**: Provider strategy registry and external provider adapters (Google, GitHub, etc.).
- **`otp/`**: One-Time Passcode state machine, attempt tracker, and expiration engine.
- **`session/`**: Session tracking, IP/User-Agent metadata logging, and active device management.
- **`state_machine/`**: User account status lifecycle enforcement (Active, Locked, Suspended, etc.).
- **`events/`**: Security audit log models and event emitter specifications.
- **`mail/`**: Transactional email templates and delivery provider abstractions.

### 2. Dependency Flow & Graph
To guarantee clean architecture and avoid circular dependencies:
- **`Controllers`** depends on **`Services`**, **`Schemas`**, and **`Interfaces`**.
- **`Services`** depends on **`Interfaces`**, **`Models`**, and **`Security`**.
- **`Interfaces`** has ZERO dependencies on internal service implementations or models.
- **`Security`** has ZERO dependencies on SQLAlchemy models or API schemas.
