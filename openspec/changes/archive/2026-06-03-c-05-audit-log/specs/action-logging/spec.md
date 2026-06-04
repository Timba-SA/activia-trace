## ADDED Requirements

### Requirement: AuditActionCode constants

The system SHALL define action code constants in `modules/audit/constants.py` as a class or enum `AuditActionCode`. Each code SHALL be a string constant. Minimum codes SHALL include: `CALIFICACIONES_IMPORTAR`, `PADRON_CARGAR`, `COMUNICACION_ENVIAR`, `ASIGNACION_MODIFICAR`, `LIQUIDACION_CERRAR`, `IMPERSONACION_INICIAR`, `IMPERSONACION_FINALIZAR`.

#### Scenario: AuditActionCode contains standard codes

- **WHEN** `AuditActionCode` is inspected
- **THEN** it SHALL contain at minimum `CALIFICACIONES_IMPORTAR`, `PADRON_CARGAR`, `COMUNICACION_ENVIAR`, `ASIGNACION_MODIFICAR`, `LIQUIDACION_CERRAR`, `IMPERSONACION_INICIAR`, `IMPERSONACION_FINALIZAR`

#### Scenario: Action codes are strings

- **WHEN** any `AuditActionCode` member is accessed
- **THEN** its value SHALL be a string (e.g., `AuditActionCode.CALIFICACIONES_IMPORTAR == "CALIFICACIONES_IMPORTAR"`)

### Requirement: AuditService for programmatic logging

The system SHALL provide `AuditService` as a FastAPI dependency that exposes a `log()` method accepting: `accion` (string), `actor_id` (UUID), `tenant_id` (UUID), `materia_id` (UUID, optional), `impersonado_id` (UUID, optional), `detalle` (dict, optional), `filas_afectadas` (int, optional), `ip` (string, optional), `user_agent` (string, optional).

#### Scenario: AuditService.log creates entry in database

- **WHEN** `AuditService.log()` is called with valid `accion`, `actor_id`, and `tenant_id`
- **THEN** a new AuditLog entry SHALL be persisted with those values

#### Scenario: AuditService.log with all optional fields

- **WHEN** `AuditService.log()` is called with `accion`, `actor_id`, `tenant_id`, plus all optional fields
- **THEN** the entry SHALL contain all provided values including `detalle` as JSONB

### Requirement: @audit_action decorator

The system SHALL provide a `@audit_action(code, extra_fields=None)` decorator for service methods. The decorator SHALL:
1. Resolve `actor_id`, `tenant_id`, `ip`, `user_agent` from `AuditContext` (injected dependency)
2. Execute the decorated method
3. Capture the return value to determine `filas_afectadas` (if the method returns an int, or has a `filas_afectadas` key in a dict return)
4. Call `AuditService.log()` with the action code and context
5. Pass through any exception from the decorated method (audit failure SHALL NOT break the primary operation)

#### Scenario: @audit_action logs after successful execution

- **WHEN** a service method decorated with `@audit_action("PADRON_CARGAR")` executes successfully
- **THEN** an AuditLog entry SHALL be created with `accion = "PADRON_CARGAR"` and the correct `actor_id` from context

#### Scenario: @audit_action captures filas_afectadas from return value

- **WHEN** a decorated method returns `{"filas_afectadas": 42}`
- **THEN** the audit log entry SHALL have `filas_afectadas = 42`

#### Scenario: @audit_action does not break on audit failure

- **WHEN** the decorated method succeeds but `AuditService.log()` raises an exception
- **THEN** the original method's result SHALL still be returned (audit failure is logged/suppressed)

#### Scenario: @audit_action passes through exceptions

- **WHEN** the decorated method raises an exception
- **THEN** the exception SHALL propagate to the caller (no audit entry is created for failed operations)
