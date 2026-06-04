## 1. AuditLog Model and Migration

- [x] 1.1 Define `AuditLog` SQLAlchemy model in `app/models/audit_log.py` with fields from E-AUD spec
- [x] 1.2 Define Pydantic schemas for AuditLog (request/response) with `extra='forbid'` in `app/schemas/audit_log.py`
- [x] 1.3 Create Alembic migration 009: create `audit_log` table with indexes on `(tenant_id, fecha_hora)`, `(actor_id)`, `(accion)`
- [x] 1.4 Add PostgreSQL append-only trigger to migration 009 (reject UPDATE and DELETE on `audit_log`)
- [x] 1.5 Implement `AuditLogRepository` with only `create()` and `find()` methods (no update/delete) in `app/repositories/audit_log_repository.py`
- [x] 1.6 Write tests for model creation, repository append-only enforcement, and migration

## 2. AuditActionCode Constants

- [x] 2.1 Define `AuditActionCode` constants in `app/core/audit_constants.py` with all standard codes
- [x] 2.2 Write tests for action code values and type

## 3. AuditService and AuditContext

- [x] 3.1 Implement `AuditContext` FastAPI dependency that extracts `actor_id`, `impersonado_id`, `ip`, `user_agent` from request/JWT
- [x] 3.2 Implement `AuditService` with `log()` method that creates AuditLog entries via repository
- [x] 3.3 Write tests for `AuditContext` under normal and impersonation sessions
- [x] 3.4 Write tests for `AuditService.log()` with various field combinations

## 4. @audit_action Decorator

- [x] 4.1 Implement `@audit_action(code)` decorator in `app/core/audit_decorator.py` that resolves context, executes method, and logs with filas_afectadas
- [x] 4.2 Ensure decorator does not break primary operation on audit failure (suppress audit errors)
- [x] 4.3 Write tests for decorator: successful logging, filas_afectadas capture, exception passthrough, audit failure resilience

## 5. Impersonation Support

- [x] 5.1 Add `impersonating_user_id` and `impersonation` claim to JWT generation logic for impersonation sessions
- [x] 5.2 Update auth middleware to detect impersonation JWT and expose claims to `AuditContext`
- [x] 5.3 Implement impersonation start/end endpoints or integrate with existing auth endpoints
- [x] 5.4 Register `IMPERSONACION_INICIAR` and `IMPERSONACION_FINALIZAR` on impersonation start/end
- [x] 5.5 Write tests for impersonation JWT structure, session detection, and audit attribution

## 6. Audit Log API Endpoint

- [x] 6.1 Implement `GET /api/audit/log` with filters (accion, actor_id, materia_id, desde, hasta) and pagination
- [x] 6.2 Apply middleware guard with `require_permission("auditoria:ver")`
- [x] 6.3 Apply tenant scope filter (results limited to current tenant)
- [x] 6.4 Write tests for filtering, pagination, permission guard, and tenant isolation

## 7. Permission Seed Update

- [x] 7.1 Add `auditoria:ver` to COORDINADOR, ADMIN, FINANZAS role seeds (in migration 009)
- [x] 7.2 Add `impersonacion:usar` to ADMIN role seed only (in migration 009)
- [x] 7.3 Write tests verifying permissions are seeded correctly

## 8. Module Wiring

- [x] 8.1 Register `AuditService` and `AuditContext` as FastAPI dependencies
- [x] 8.2 Include audit router in main FastAPI app
- [x] 8.3 Verify end-to-end: action logged via decorator → visible via GET endpoint
