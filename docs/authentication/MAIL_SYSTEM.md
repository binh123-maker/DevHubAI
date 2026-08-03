# DevHub AI - Transactional Mail System Specification (Phase 3)

## Overview
The `MailService` handles transactional email delivery across DevHub AI for OTP codes, password resets, and security alerts.

---

## SMTP Configuration & Fallback Driver (Parts 3 & 26)

| Setting Name | Environment Key | Default | Description |
| :--- | :--- | :--- | :--- |
| `smtp_host` | `SMTP_HOST` | `"localhost"` | Hostname of SMTP relay server |
| `smtp_port` | `SMTP_PORT` | `587` | SMTP port (587 TLS / 465 SSL / 25) |
| `smtp_username` | `SMTP_USERNAME` | `""` | Authentication username |
| `smtp_password` | `SMTP_PASSWORD` | `""` | Authentication password |
| `smtp_from_email` | `SMTP_FROM_EMAIL` | `"noreply@devhub.ai"` | Sender address |
| `smtp_tls` | `SMTP_TLS` | `True` | Enable TLS encryption |

---

## Development Mode Fallback
When SMTP credentials are empty or `smtp_host` is `"localhost"`, `MailService` operates in **Console Log Fallback Mode**. Transactional emails and OTP codes are printed directly to the application console logger, enabling offline testing without requiring a live SMTP relay.
