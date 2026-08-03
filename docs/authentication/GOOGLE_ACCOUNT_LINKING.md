# DevHub AI - Google Account Linking & Conflict Resolution Rules

## Secure Linking Rules

1. **One-to-One Mapping**: One Google `sub` (provider_user_id) maps to exactly one DevHub `User.id`.
2. **Verified Email Match**: If a Google login matches an existing active DevHub user's email, the system links the Google account to the existing user instead of creating a duplicate account.
3. **Inactive User Protection**: If the matching local user is inactive or suspended, automatic linking is strictly rejected.
4. **Duplicate Prevention**: Attempting to link a Google account that is already associated with another DevHub user raises a `409 Conflict` error.
5. **Sole Authentication Method Protection**: Users cannot disconnect their Google account if it is their only registered authentication method and no password is set.
