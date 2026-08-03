# DevHub AI - Authentication Architecture Blueprint & Documentation Index

Welcome to the official Authentication Architecture Blueprint for DevHub AI. This index serves as the master entry point and navigation guide for all authentication documentation, security policies, state machines, API standards, and migration roadmaps.

---

## Document Index & Reading Order

For onboarding developers, architects, and security auditors, follow the recommended reading order below:

### 1. Architectural Blueprint & Overview
- [AUTH_ARCHITECTURE.md](AUTH_ARCHITECTURE.md) - System overview, component boundaries, dependency rules.
- [AUTH_DECISIONS.md](AUTH_DECISIONS.md) - Architectural Decision Record (ADR) for Google-Only Authentication.
- [ARCHITECTURE_FREEZE.md](ARCHITECTURE_FREEZE.md) - Immutable architecture freeze declaration & extension rules.
- [PHASE2_CONTRACT.md](PHASE2_CONTRACT.md) - Strict Phase 2 developer implementation contract.

### 2. Configurations, Constants & Error Systems
- [AUTH_CONFIGURATION.md](AUTH_CONFIGURATION.md) - Centralized configuration parameters & classification.
- [AUTH_FEATURE_FLAGS.md](AUTH_FEATURE_FLAGS.md) - Authentication feature flag specifications.
- [AUTH_CONSTANTS.md](AUTH_CONSTANTS.md) - Strongly typed authentication enums & constants.
- [AUTH_ERROR_CODES.md](AUTH_ERROR_CODES.md) - Master namespaced error code catalog.
- [AUTH_RESPONSE_STANDARD.md](AUTH_RESPONSE_STANDARD.md) - Versioned API response envelope specification.

### 3. State Machines & Subsystems
- [ACCOUNT_STATE_MACHINE.md](ACCOUNT_STATE_MACHINE.md) - User account lifecycle state machine.
- [OTP_STATE_MACHINE.md](OTP_STATE_MACHINE.md) - Unified OTP module state machine.
- [SESSION_STATE_MACHINE.md](SESSION_STATE_MACHINE.md) - Device & Session management state machine.
- [OAUTH_STATE_MACHINE.md](OAUTH_STATE_MACHINE.md) - Google OAuth strategy flow state machine.
- [OAUTH_DESIGN.md](OAUTH_DESIGN.md) - Google Identity Integration architecture.
- [ACCOUNT_LINKING.md](ACCOUNT_LINKING.md) - Account linking & conflict resolution.
- [GOOGLE_OAUTH.md](GOOGLE_OAUTH.md) - Google OAuth 2.0 integration & Identity-Only Policy.
- [GOOGLE_API.md](GOOGLE_API.md) - Google OAuth API specifications.
- [GOOGLE_SEQUENCE.md](GOOGLE_SEQUENCE.md) - Google OAuth sequence diagrams.
- [GOOGLE_SECURITY.md](GOOGLE_SECURITY.md) - Google OAuth security controls.
- [GOOGLE_DATABASE.md](GOOGLE_DATABASE.md) - `oauth_accounts` table DDL & index specs.
- [GOOGLE_TESTING.md](GOOGLE_TESTING.md) - Google OAuth testing matrix & mocks.
- [GOOGLE_UI_FLOW.md](GOOGLE_UI_FLOW.md) - Google OAuth frontend UI & callback flow.
- [GOOGLE_ACCOUNT_LINKING.md](GOOGLE_ACCOUNT_LINKING.md) - Secure account linking rules.
- [GOOGLE_PROFILE_SYNC.md](GOOGLE_PROFILE_SYNC.md) - Non-destructive profile sync policy.
- [OAUTH_PROVIDER_GUIDE.md](OAUTH_PROVIDER_GUIDE.md) - Developer guide for Google Identity Integration.

### 4. Security Policies & Cross-Cutting Concerns
- [SECURITY_AUDIT.md](SECURITY_AUDIT.md) - OWASP Top 10 vulnerability assessment & threat models.
- [PASSWORD_POLICY.md](PASSWORD_POLICY.md) - Password strength, hashing, and rotation rules.
- [TOKEN_POLICY.md](TOKEN_POLICY.md) - JWT & Refresh Token rotation policy.
- [OTP_POLICY.md](OTP_POLICY.md) - OTP rate limits, TTLs, and lock policies.
- [SESSION_POLICY.md](SESSION_POLICY.md) - Device tracking & concurrent session limits.
- [PERMISSION_FOUNDATION.md](PERMISSION_FOUNDATION.md) - RBAC & authorization boundary design.
- [CORRELATION_ID_ARCHITECTURE.md](CORRELATION_ID_ARCHITECTURE.md) - Request correlation ID tracing architecture.
- [SECURITY_EVENTS.md](SECURITY_EVENTS.md) - Audit trail event types & severity levels.
- [MAIL_SYSTEM.md](MAIL_SYSTEM.md) - Transactional mail templates & delivery contracts.

### 5. Testing, Migrations & Validation
- [DATABASE_DESIGN.md](DATABASE_DESIGN.md) - Future DDL schema specifications.
- [API_DESIGN.md](API_DESIGN.md) - OpenAPI endpoints specification.
- [MIGRATION_PLAN.md](MIGRATION_PLAN.md) - Versioned Alembic migration roadmap (V1 to V5).
- [AUTH_TEST_MATRIX.md](AUTH_TEST_MATRIX.md) - Comprehensive testing & resilience fault matrix.
- [PHASE_1_5_DONE.md](PHASE_1_5_DONE.md) - Definition of Done verification checklist.
- [FOUNDATION_VALIDATION_REPORT.md](FOUNDATION_VALIDATION_REPORT.md) - Final Phase Readiness Certification & Score.
