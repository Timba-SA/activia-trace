## ADDED Requirements

### Requirement: Login with email and password

The system SHALL provide a `POST /api/auth/login` endpoint that authenticates users with email and Argon2id-verified password. On success, the system SHALL issue a JWT access token (15 min TTL) and an opaque refresh token (7 days TTL). The access token SHALL contain claims: `sub` (user UUID), `tenant_id` (UUID), `roles` (list of strings), `exp` (expiration), `iat` (issued at). If the user has 2FA enabled, the endpoint SHALL return a short-lived `temp_token` (5 min) instead of the session tokens, requiring a subsequent 2FA verification.

#### Scenario: Login with valid credentials without 2FA

- **WHEN** a POST request is sent to `/api/auth/login` with valid `email` and `password` for a user that does NOT have 2FA enabled
- **THEN** the response SHALL include `access_token` (JWT, exp in 15 min), `refresh_token` (opaque), `token_type: "bearer"`, and `expires_in` (seconds)

#### Scenario: Login with invalid credentials

- **WHEN** a POST request is sent to `/api/auth/login` with an incorrect password
- **THEN** the response SHALL be `401 Unauthorized` with an error message

#### Scenario: Login with nonexistent email

- **WHEN** a POST request is sent to `/api/auth/login` with an email that does not exist
- **THEN** the response SHALL be `401 Unauthorized` (same error as invalid password — no user enumeration)

#### Scenario: Login for inactive user

- **WHEN** a POST request is sent to `/api/auth/login` for a user with `is_active = False`
- **THEN** the response SHALL be `401 Unauthorized`

#### Scenario: Login with valid credentials with 2FA enabled

- **WHEN** a POST request is sent to `/api/auth/login` with valid credentials for a user that HAS 2FA enabled
- **THEN** the response SHALL include `temp_token` (JWT, exp in 5 min), `requires_2fa: True`, and no session tokens

### Requirement: 2FA login verification

The system SHALL provide a `POST /api/auth/login/2fa` endpoint that accepts a `temp_token` and a TOTP code. If the TOTP code is valid, the system SHALL issue access and refresh tokens. The temp_token SHALL be a JWT carrying `sub` (user_id), `pending_2fa: True`, and short expiry (5 min). A used or expired temp_token SHALL be rejected.

#### Scenario: Valid TOTP code with valid temp_token

- **WHEN** a POST request is sent to `/api/auth/login/2fa` with a valid `temp_token` and a valid TOTP `code`
- **THEN** the response SHALL include `access_token`, `refresh_token`, and `token_type: "bearer"`

#### Scenario: Invalid TOTP code

- **WHEN** a POST request is sent to `/api/auth/login/2fa` with a valid `temp_token` and an invalid TOTP `code`
- **THEN** the response SHALL be `401 Unauthorized`

#### Scenario: Expired or reused temp_token

- **WHEN** a POST request is sent to `/api/auth/login/2fa` with an expired or already-used `temp_token`
- **THEN** the response SHALL be `401 Unauthorized`

### Requirement: Token refresh with rotation

The system SHALL provide a `POST /api/auth/refresh` endpoint that accepts a valid refresh token. On success, it SHALL invalidate the old refresh token (mark session as revoked) and issue a new access token + new refresh token. If an already-revoked refresh token is presented (detected reuse), the system SHALL revoke ALL sessions for that user as a fraud containment measure.

#### Scenario: Successful refresh

- **WHEN** a POST request is sent to `/api/auth/refresh` with a valid, non-revoked refresh token
- **THEN** the old refresh token SHALL be invalidated, and the response SHALL include a new `access_token` and `refresh_token`

#### Scenario: Refresh with revoked token (reuse detection)

- **WHEN** a POST request is sent to `/api/auth/refresh` with a refresh token that has already been used (revoked)
- **THEN** ALL sessions for that user SHALL be revoked, and the response SHALL be `401 Unauthorized`

#### Scenario: Refresh with expired token

- **WHEN** a POST request is sent to `/api/auth/refresh` with an expired refresh token
- **THEN** the response SHALL be `401 Unauthorized`

### Requirement: Logout

The system SHALL provide a `POST /api/auth/logout` endpoint that revokes the current session (invalidates the refresh token). The endpoint SHALL require authentication (valid access token).

#### Scenario: Successful logout

- **WHEN** an authenticated POST request is sent to `/api/auth/logout`
- **THEN** the current session SHALL be revoked, and the response SHALL be `200 OK`

### Requirement: get_current_user dependency

The system SHALL provide a FastAPI dependency `get_current_user` that extracts the `Authorization: Bearer <token>` header, verifies the JWT, and returns a `CurrentUser` object with `id` (UUID), `tenant_id` (UUID), `email` (string), `roles` (list of strings), and `is_active` (boolean). If the token is missing, expired, or invalid, the dependency SHALL raise `HTTPException 401`.

#### Scenario: Valid token returns current user

- **WHEN** a request includes a valid `Authorization: Bearer <access_token>` header
- **THEN** the dependency returns a `CurrentUser` with the user's `id`, `tenant_id`, `email`, `roles`, and `is_active`

#### Scenario: Missing token returns 401

- **WHEN** a request does NOT include an `Authorization` header
- **THEN** the dependency raises `HTTPException 401`

#### Scenario: Expired token returns 401

- **WHEN** a request includes an expired access token
- **THEN** the dependency raises `HTTPException 401`

#### Scenario: Identity cannot be overridden by request parameters

- **WHEN** a request includes a valid token AND also provides `user_id` or `tenant_id` in URL query string, body, or headers
- **THEN** the `CurrentUser` SHALL be derived exclusively from the token; any request-provided identifiers SHALL be ignored for identity resolution

### Requirement: Inactive user rejected at dependency level

The `get_current_user` dependency SHALL verify that `is_active = True` for the user. If the user has been deactivated after token issuance, the dependency SHALL raise `HTTPException 401`.

#### Scenario: Deactivated user with valid token

- **WHEN** a user with `is_active = False` presents a valid (but issued before deactivation) access token
- **THEN** the `get_current_user` dependency raises `HTTPException 401`
