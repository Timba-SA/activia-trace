## ADDED Requirements

### Requirement: AuditLog model

The system SHALL provide an `AuditLog` model (E-AUD) with the following fields: `id` (UUID PK), `tenant_id` (UUID FK, NOT NULL), `fecha_hora` (datetime, NOT NULL), `actor_id` (UUID FK to Usuario, NOT NULL), `impersonado_id` (UUID FK to Usuario, nullable), `materia_id` (UUID FK to Materia, nullable), `accion` (string, NOT NULL — action code like `CALIFICACIONES_IMPORTAR`), `detalle` (JSONB, nullable), `filas_afectadas` (integer, default 0), `ip` (string, nullable), `user_agent` (string, nullable). The model SHALL have composite indexes on `(tenant_id, fecha_hora)`, `(actor_id)`, and `(accion)`.

#### Scenario: Create AuditLog entry with all fields

- **WHEN** a new AuditLog entry is created with valid `tenant_id`, `actor_id`, `accion`, `fecha_hora`, and optional `materia_id`, `detalle`, `filas_afectadas`, `ip`, `user_agent`
- **THEN** the entry SHALL be persisted with all provided values

#### Scenario: AuditLog entry with minimal required fields

- **WHEN** a new AuditLog entry is created with only `tenant_id`, `actor_id`, `accion`, and `fecha_hora`
- **THEN** the entry SHALL be persisted with `filas_afectadas` defaulting to 0, and nullable fields as NULL

#### Scenario: AuditLog entry assigned to a materia

- **WHEN** an audit log entry is created with a valid `materia_id`
- **THEN** the materia association SHALL be stored and queryable

### Requirement: Append-only enforcement at database level

The system SHALL enforce append-only behavior on the `audit_log` table via a PostgreSQL trigger. Any UPDATE or DELETE operation on the `audit_log` table SHALL be rejected with an error. INSERT operations SHALL be allowed normally.

#### Scenario: UPDATE on audit_log is rejected

- **WHEN** an UPDATE statement is executed against the `audit_log` table
- **THEN** the database SHALL raise an error and the update SHALL be rejected

#### Scenario: DELETE on audit_log is rejected

- **WHEN** a DELETE statement is executed against the `audit_log` table
- **THEN** the database SHALL raise an error and the delete SHALL be rejected

#### Scenario: INSERT on audit_log is allowed

- **WHEN** an INSERT statement is executed against the `audit_log` table
- **THEN** the insert SHALL succeed and the row SHALL be persisted

### Requirement: Append-only enforcement at application level

The `AuditLogRepository` SHALL expose only `create()` and `find()` methods. No `update()` or `delete()` methods SHALL be available.

#### Scenario: AuditLogRepository has no update method

- **WHEN** the `AuditLogRepository` class is inspected
- **THEN** it SHALL NOT have an `update()` method

#### Scenario: AuditLogRepository has no delete method

- **WHEN** the `AuditLogRepository` class is inspected
- **THEN** it SHALL NOT have a `delete()` method

### Requirement: Migration 003 — audit_log table

The system SHALL provide Alembic migration 003 that creates the `audit_log` table with all fields, indexes, and the append-only trigger. The migration SHALL be reversible (downgrade drops the table and trigger).

#### Scenario: Migration 003 creates audit_log table

- **WHEN** migration 003 is applied
- **THEN** the `audit_log` table SHALL exist with columns: id, tenant_id, fecha_hora, actor_id, impersonado_id, materia_id, accion, detalle, filas_afectadas, ip, user_agent

#### Scenario: Migration 003 creates append-only trigger

- **WHEN** migration 003 is applied
- **THEN** a trigger SHALL exist on the `audit_log` table that rejects UPDATE and DELETE

#### Scenario: Migration 003 downgrade removes audit_log table

- **WHEN** migration 003 is rolled back
- **THEN** the `audit_log` table and its trigger SHALL be removed

### Requirement: AuditLog list endpoint with pagination and filters

The system SHALL provide `GET /api/audit/log` returning paginated audit log entries. The endpoint SHALL support query parameters: `accion` (string, exact match), `actor_id` (UUID, exact match), `materia_id` (UUID, exact match), `desde` (datetime, start of range), `hasta` (datetime, end of range), `limit` (integer, default 20, max 100), `offset` (integer, default 0). The endpoint SHALL be guarded by `require_permission("auditoria:ver")` and SHALL scope results to the current tenant.

#### Scenario: List audit log filtered by accion

- **WHEN** a user with `auditoria:ver` sends GET to `/api/audit/log?accion=CALIFICACIONES_IMPORTAR`
- **THEN** the response SHALL include only entries with that exact action code

#### Scenario: List audit log filtered by date range

- **WHEN** a user with `auditoria:ver` sends GET to `/api/audit/log?desde=2026-01-01&hasta=2026-01-31`
- **THEN** the response SHALL include only entries with `fecha_hora` within that range

#### Scenario: List audit log with pagination

- **WHEN** a user sends GET to `/api/audit/log?limit=10&offset=0`
- **THEN** the response SHALL return at most 10 entries with `total` and `pages` metadata

#### Scenario: List audit log without auditoria:ver returns 403

- **WHEN** a user WITHOUT `auditoria:ver` sends GET to `/api/audit/log`
- **THEN** the response SHALL be `403 Forbidden`

#### Scenario: Audit log list is scoped to tenant

- **WHEN** a user from tenant A sends GET to `/api/audit/log`
- **THEN** the response SHALL NOT include entries from tenant B
