# DevHub AI - Multi-Provider Account Linking Architecture

## Strategy & Conflict Resolution

The Account Linking subsystem allows a single user account (`users.id`) to link multiple authentication methods (Email/Password, Google, GitHub, Microsoft).

## Key Principles & Business Rules
1. **Primary Email Identification**: User identity is anchored by verified primary email.
2. **Duplicate Prevention**: If an OAuth provider returns a verified email matching an existing local account, the system automatically links the provider to the existing user after verifying email ownership.
3. **Primary Login Method**: Users can establish a primary login method while retaining fallback methods.
4. **Unlink Constraints**: A user cannot unlink their last remaining authentication method (prevents orphaned accounts).
