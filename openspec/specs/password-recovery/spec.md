## ADDED Requirements

### Requirement: Forgot password — generate recovery token

The system SHALL provide a `POST /api/auth/forgot` endpoint that accepts an `email`. If the email belongs to an active user, the system SHALL generate a single-use recovery token (random 32-byte hex string), store its SHA-256 hash in the `RecoveryToken` table with a 15-minute expiry, and return the raw token in the response (for MVP; production will send it via email). The endpoint SHALL always return `200 OK` even if the email does not exist, to prevent user enumeration.

#### Scenario: Forgot password for existing email

- **WHEN** a POST request is sent to `/api/auth/forgot` with an `email` that belongs to an active user
- **THEN** a `RecoveryToken` SHALL be created with `token_hash`, `expires_at` (15 min from now), `used_at = NULL`, and the raw token SHALL be returned in the response

#### Scenario: Forgot password for nonexistent email

- **WHEN** a POST request is sent to `/api/auth/forgot` with an `email` that does not exist
- **THEN** the response SHALL be `200 OK` (same as existing email — no user enumeration)

#### Scenario: Forgot password for inactive user

- **WHEN** a POST request is sent to `/api/auth/forgot` with an `email` of an inactive user
- **THEN** the response SHALL be `200 OK` (no user enumeration), and NO recovery token SHALL be created

### Requirement: Reset password with recovery token

The system SHALL provide a `POST /api/auth/reset` endpoint that accepts a `token` (raw recovery token), `email`, and `new_password`. If the token's hash matches, the token has not been used, and the token has not expired, the system SHALL update the user's password (hashed with Argon2id) and mark the token as used (`used_at = now()`). The new password SHALL be at least 8 characters.

#### Scenario: Successful password reset

- **WHEN** a POST request is sent to `/api/auth/reset` with a valid `token`, matching `email`, and a `new_password` of at least 8 characters
- **THEN** the user's password SHALL be updated (Argon2id hash), the token SHALL be marked as used, and the response SHALL be `200 OK`

#### Scenario: Reset with used token

- **WHEN** a POST request is sent to `/api/auth/reset` with a token that has already been used
- **THEN** the response SHALL be `400 Bad Request`

#### Scenario: Reset with expired token

- **WHEN** a POST request is sent to `/api/auth/reset` with a token past its `expires_at`
- **THEN** the response SHALL be `400 Bad Request`

#### Scenario: Reset with mismatched email

- **WHEN** a POST request is sent to `/api/auth/reset` with a token that belongs to a different email
- **THEN** the response SHALL be `400 Bad Request`

#### Scenario: Reset with short password

- **WHEN** a POST request is sent to `/api/auth/reset` with a `new_password` shorter than 8 characters
- **THEN** the response SHALL be `422 Unprocessable Entity` with a validation error

### Requirement: Recovery token model

The `RecoveryToken` model SHALL contain: `id` (UUID, PK), `user_id` (FK → Usuario), `token_hash` (string, SHA-256 of raw token), `expires_at` (datetime, timezone-aware), `used_at` (datetime, nullable). A token is valid only if `used_at IS NULL` AND `expires_at > now()`.

#### Scenario: Token expires after 15 minutes

- **WHEN** a recovery token is created
- **THEN** its `expires_at` SHALL be exactly 15 minutes from the creation time
