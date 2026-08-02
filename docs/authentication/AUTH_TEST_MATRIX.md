# DevHub AI - Authentication & Resilience Testing Matrix

## Overview

This matrix defines the test coverage across functional, integration, security, resilience, and performance scenarios for the authentication engine.

---

## Comprehensive Test Matrix

| Test ID | Scenario Description | Category | Expected Result | Pass Criteria | Priority | Automation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TEST-01** | Register new user with valid data | Integration | HTTP 201 Created + Token pair | User & Profile created in DB | P0 | Automated |
| **TEST-02** | Register with duplicate email | Integration | HTTP 409 Conflict | `AUTH_ACCOUNT_001` error returned | P0 | Automated |
| **TEST-03** | Register with password mismatch | Unit / API | HTTP 422 Unprocessable | Validation error | P0 | Automated |
| **TEST-04** | Login with valid credentials | Integration | HTTP 200 OK + Token pair | Refresh token hashed in DB | P0 | Automated |
| **TEST-05** | Login with invalid password | Integration | HTTP 401 Unauthorized | `AUTH_LOGIN_001` error | P0 | Automated |
| **TEST-06** | Rotate refresh token | Integration | HTTP 200 OK + New Tokens | Old token revoked, new token active | P0 | Automated |
| **TEST-07** | Use revoked refresh token | Security | HTTP 401 Unauthorized | `AUTH_TOKEN_004` error | P0 | Automated |
| **TEST-08** | Access `/me` without Bearer token | API | HTTP 401 Unauthorized | Unauthenticated detail | P0 | Automated |
| **TEST-09** | Database unavailable fault | Resilience | HTTP 500 / Retry | Graceful error, zero crash | P1 | Manual/CI |
| **TEST-10** | Expired Access Token | JWT | Interceptor triggers refresh | Auto-recovery to 200 OK | P0 | Automated |
| **TEST-11** | Concurrent login requests | Performance | All sessions created cleanly | No race condition or DB lock | P1 | Automated |
| **TEST-12** | Open Redirect input in `LoginPage` | Security | Redirect sanitized to `/workspaces` | No external URL redirect | P0 | Automated |
