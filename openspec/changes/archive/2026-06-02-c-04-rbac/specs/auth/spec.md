## MODIFIED Requirements

### Requirement: get_current_user dependency

The system SHALL provide a FastAPI dependency `get_current_user` that extracts the `Authorization: Bearer <token>` header, verifies the JWT, and returns a `CurrentUser` object with `id` (UUID), `tenant_id` (UUID), `email` (string), `roles` (list of strings), `permissions` (frozenset of strings), and `is_active` (boolean). The `permissions` field SHALL be resolved by loading all roles assigned to the user via the `usuario_role` junction and computing the set union of their `permissions` lists. If the token is missing, expired, or invalid, the dependency SHALL raise `HTTPException 401`.

#### Scenario: Valid token returns current user with permissions

- **WHEN** a request includes a valid `Authorization: Bearer <access_token>` header for a user with assigned roles
- **THEN** the dependency returns a `CurrentUser` with the user's `id`, `tenant_id`, `email`, `roles`, `permissions` (resolved from role assignments), and `is_active`

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
