## ADDED Requirements

### Requirement: Impersonation session is distinguishable

When a user impersonates another user, the system SHALL generate a JWT that includes both `user_id` (the impersonated user) and `impersonating_user_id` (the real actor). The token SHALL also include an `impersonation = true` claim. All downstream code SHALL be able to detect that the current session is an impersonation session.

#### Scenario: Impersonation JWT has impersonation flag

- **WHEN** a JWT is generated for an impersonation session
- **THEN** the token SHALL contain `impersonation: true`, `user_id: <impersonated>`, and `impersonating_user_id: <actor>`

#### Scenario: Normal JWT has no impersonation fields

- **WHEN** a JWT is generated for a normal (non-impersonated) session
- **THEN** the token SHALL NOT contain `impersonation` or `impersonating_user_id` claims

### Requirement: Audit context exposes impersonation info

The system SHALL provide `AuditContext` (FastAPI dependency) that exposes `actor_id`, `impersonated_user_id`, `ip`, and `user_agent`. When the session is impersonated, `actor_id` SHALL be the real actor (`impersonating_user_id` from JWT) and `impersonated_user_id` SHALL be the target user. When the session is normal, `actor_id` SHALL equal the JWT's `user_id` and `impersonated_user_id` SHALL be None.

#### Scenario: AuditContext under impersonation

- **WHEN** a request is made with an impersonation JWT
- **THEN** `AuditContext.actor_id` SHALL be the value of `impersonating_user_id` and `AuditContext.impersonated_user_id` SHALL be the value of `user_id`

#### Scenario: AuditContext under normal session

- **WHEN** a request is made with a normal JWT
- **THEN** `AuditContext.actor_id` SHALL be the JWT's `user_id` and `AuditContext.impersonated_user_id` SHALL be None

### Requirement: Impersonation start/end is audited

When an impersonation session starts or ends, the system SHALL automatically log an audit entry with codes `IMPERSONACION_INICIAR` and `IMPERSONACION_FINALIZAR` respectively. The `detalle` field SHALL include both the actor's and target user's IDs and usernames.

#### Scenario: Start impersonation logs IMPERSONACION_INICIAR

- **WHEN** a user with `impersonacion:usar` starts an impersonation session targeting another user
- **THEN** an AuditLog entry SHALL be created with `accion = "IMPERSONACION_INICIAR"` and `detalle` containing both actor and target user info

#### Scenario: End impersonation logs IMPERSONACION_FINALIZAR

- **WHEN** an impersonation session ends (logout or explicit stop)
- **THEN** an AuditLog entry SHALL be created with `accion = "IMPERSONACION_FINALIZAR"`

### Requirement: Impersonation requires explicit permission

The system SHALL guard impersonation endpoints with `require_permission("impersonacion:usar")`. A user without this permission SHALL NOT be able to impersonate another user.

#### Scenario: Impersonation without permission returns 403

- **WHEN** a user WITHOUT `impersonacion:usar` attempts to start an impersonation session
- **THEN** the system SHALL return `403 Forbidden`

#### Scenario: Impersonation with permission succeeds

- **WHEN** a user WITH `impersonacion:usar` attempts to start an impersonation session
- **THEN** the system SHALL create the impersonation session and return a valid impersonation JWT

### Requirement: Permission seed includes auditoria:ver and impersonacion:usar

The system SHALL seed the permissions `auditoria:ver` and `impersonacion:usar` in the existing role seed mechanism. `auditoria:ver` SHALL be assigned to COORDINADOR, ADMIN, and FINANZAS roles. `impersonacion:usar` SHALL be assigned to ADMIN role only.

#### Scenario: auditoria:ver is seeded for COORDINADOR

- **WHEN** the seed migration runs and COORDINADOR role permissions are inspected
- **THEN** `auditoria:ver` SHALL be included

#### Scenario: auditoria:ver is seeded for ADMIN

- **WHEN** the seed migration runs and ADMIN role permissions are inspected
- **THEN** `auditoria:ver` SHALL be included

#### Scenario: auditoria:ver is seeded for FINANZAS

- **WHEN** the seed migration runs and FINANZAS role permissions are inspected
- **THEN** `auditoria:ver` SHALL be included

#### Scenario: impersonacion:usar is seeded for ADMIN

- **WHEN** the seed migration runs and ADMIN role permissions are inspected
- **THEN** `impersonacion:usar` SHALL be included

#### Scenario: impersonacion:usar is NOT seeded for non-ADMIN roles

- **WHEN** the seed migration runs and non-ADMIN role permissions are inspected
- **THEN** `impersonacion:usar` SHALL NOT be included
