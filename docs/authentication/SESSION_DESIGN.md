# DevHub AI - Session & Device Management Architecture

## Overview

The Session Management subsystem tracks active user sessions, device footprints, IP addresses, user-agent details, and login timestamps to support active device listing and remote session revocation.

## Key Operational Capabilities
1. **Multi-Device Session Tracking**: Each login generates a unique record in `login_sessions`.
2. **Device Fingerprinting**: Captures IP address, operating system, browser, and device model.
3. **Single Session Revocation**: User can terminate any suspicious session remotely.
4. **Global Logout**: User can terminate all active sessions across all devices on password change or security alert.
5. **Session Heartbeat**: `last_active_at` timestamp is updated during refresh token rotation.
