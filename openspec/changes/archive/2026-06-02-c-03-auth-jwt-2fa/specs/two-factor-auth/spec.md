## ADDED Requirements

### Requirement: TOTP enrollment

The system SHALL provide a `POST /api/auth/2fa/enroll` endpoint (authenticated) that generates a new TOTP secret for the current user, encrypts it with AES-256 using the `encrypt_value` utility from C-02, stores the encrypted secret, and returns the provisioning URI (otpauth://) and a base32-encoded secret for the authenticator app. The user SHALL NOT have 2FA already enabled to enroll.

#### Scenario: Successful enrollment

- **WHEN** an authenticated user without 2FA enabled requests enrollment
- **THEN** the response SHALL include a `secret` (base32), a `provisioning_uri` (otpauth:// format), and the `totp_secret` SHALL be stored encrypted

#### Scenario: Enroll when already enabled

- **WHEN** an authenticated user with 2FA already enabled requests enrollment
- **THEN** the response SHALL be `409 Conflict`

#### Scenario: Unauthenticated enrollment

- **WHEN** an unauthenticated request is sent to enroll
- **THEN** the response SHALL be `401 Unauthorized`

### Requirement: Verify TOTP and enable 2FA

The system SHALL provide a `POST /api/auth/2fa/verify` endpoint (authenticated) that accepts a TOTP `code`. If the code is valid against the stored (decrypted) TOTP secret, the system SHALL set `is_2fa_enabled = True` for the user.

#### Scenario: Successful verification

- **WHEN** an authenticated user submits a valid TOTP `code` matching their enrolled secret
- **THEN** `is_2fa_enabled` SHALL be set to `True`, and the response SHALL be `200 OK`

#### Scenario: Invalid code

- **WHEN** an authenticated user submits an invalid TOTP `code`
- **THEN** the response SHALL be `400 Bad Request` with an error message
- **AND** `is_2fa_enabled` SHALL remain `False`

### Requirement: Disable 2FA

The system SHALL provide a `POST /api/auth/2fa/disable` endpoint (authenticated) that disables 2FA for the current user by setting `is_2fa_enabled = False` and clearing the encrypted `totp_secret`.

#### Scenario: Successful disable

- **WHEN** an authenticated user with 2FA enabled requests to disable it
- **THEN** `is_2fa_enabled` SHALL be set to `False`, `totp_secret` SHALL be cleared, and the response SHALL be `200 OK`

### Requirement: TOTP verification uses pyotp library

The system SHALL use the `pyotp` library for TOTP generation and verification. The TOTP SHALL use default parameters: SHA-1, 30-second window, 6-digit codes. Verification SHALL allow a 1-step window drift (current ± 30 seconds) to accommodate clock skew.

#### Scenario: TOTP code verification with clock skew tolerance

- **WHEN** a user generates a TOTP code and submits it within ±30 seconds of validity
- **THEN** the verification SHALL succeed
