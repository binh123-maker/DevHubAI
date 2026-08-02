# DevHub AI - Security Event Logging Architecture

## Overview

The Security Event system records structured audit logs for all security actions across the application.

## Event Types & Severity Levels

| Event Type | Severity | Description |
| :--- | :--- | :--- |
| `LOGIN_SUCCESS` | `INFO` | Successful credential or OAuth login. |
| `LOGIN_FAILED` | `WARNING` | Invalid password or unknown email attempt. |
| `PASSWORD_RESET` | `WARNING` | Password reset executed successfully. |
| `ACCOUNT_LINKED` | `INFO` | New OAuth provider attached to account. |
| `SESSION_REVOKED` | `INFO` | Active session manually terminated. |
| `ACCOUNT_LOCKED` | `CRITICAL` | Account locked due to repeated brute-force attempts. |
