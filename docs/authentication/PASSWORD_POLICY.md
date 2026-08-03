# DevHub AI - Password Policy & Password History Specification (Phase 3)

## Overview
This document details the Password Policy and Password History enforcement rules implemented in Phase 3.

---

## Password Policy Rules (Part 8)
Every password set via Registration, Reset Password, or Change Password must satisfy all rules:

1. **Length:** Minimum 8 characters, maximum 128 characters.
2. **Uppercase:** At least one uppercase letter (`A-Z`).
3. **Lowercase:** At least one lowercase letter (`a-z`).
4. **Digit:** At least one numeric digit (`0-9`).
5. **Special Character:** At least one special character (`!@#$%^&*()_+-=[]{};':"|,.<>/?`).

---

## Password History Enforcement (Part 18)
- **Table:** `password_history` (`id`, `user_id`, `password_hash`, `created_at`).
- **History Depth:** Stores the last **5** password hashes per user (`PASSWORD_HISTORY_LIMIT=5`).
- **Enforcement:** When setting a new password, the hash is compared against the user's current password and all 5 historical entries. If a match is detected, the request is rejected with `HTTP 400 ("You cannot reuse a recently used password.")`.
- **Pruning:** Entries exceeding the history limit are automatically purged.
