# DevHub AI - Official Password Security Policy

## Policy Standards & Requirements

### 1. Password Complexity Rules
- **Minimum Length**: 8 characters (12+ characters strongly recommended).
- **Maximum Length**: 128 characters.
- **Character Requirements**: At least 1 uppercase letter (`A-Z`), 1 numeric digit (`0-9`), and 1 special character (`!@#$%^&*`).

### 2. Cryptographic Storage & Hashing
- **Algorithm**: `bcrypt` with cost factor / rounds = 12.
- **Salting**: Automatic unique salt generated per password by `passlib`.
- **Plaintext Prohibition**: Plaintext passwords must NEVER be logged, cached, or persisted.

### 3. Password Reset & Rotation
- **Forgot Password**: Verification code dispatched via OTP. Password reset invalidates all existing active sessions for that user.
- **Brute-Force Lockout**: 5 failed password attempts trigger a 15-minute account lockout.
