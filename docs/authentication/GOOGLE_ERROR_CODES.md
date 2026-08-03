# DevHub AI - Google OAuth Error Code Reference

## Error Mapping Matrix

| Scenario | HTTP Status | Error Detail Message | Resolution / Recovery |
| :--- | :--- | :--- | :--- |
| Unverified Google Email | 400 | "Unverified Google accounts are not permitted to log in" | Verify email address inside Google Account settings. |
| Provider Exchange Failed | 502 | "Failed to exchange authorization code with Google" | Retry OAuth handshake. |
| Provider Profile Failed | 502 | "Failed to fetch user profile from Google" | Retry OAuth handshake. |
| Already Linked Mismatch | 409 | "Google account is already linked to another user profile" | Log in with original DevHub account. |
| Sole Auth Unlink Attempt | 400 | "Cannot disconnect your sole authentication method" | Set password or link another provider first. |
