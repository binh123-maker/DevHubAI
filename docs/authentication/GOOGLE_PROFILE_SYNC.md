# DevHub AI - Non-Destructive Profile Synchronization Policy

## Synchronization Policy (Part 20)

### 1. First Login Sync
When a user logs in via Google for the first time or links a Google account:
- `full_name` is populated from Google profile if empty.
- `avatar_url` is populated from Google profile picture URL if empty.

### 2. Manual Override Preservation
If the user subsequently modifies their display name or avatar URL inside DevHub AI Settings, subsequent Google logins **MUST NOT overwrite** local profile customizations.

### 3. Last Sync Audit
`oauth_accounts.last_sync_at` is updated on every login to track identity handshake timestamps.
