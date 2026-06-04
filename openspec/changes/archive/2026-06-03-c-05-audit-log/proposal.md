## Why

activia-trace requiere un registro inmutable y auditable de toda acción significativa en la plataforma. Sin un audit log centralizado, es imposible rastrear quién hizo qué, cuándo y sobre qué entidad — requisito regulatorio y de transparencia para una plataforma multi-tenant que gestiona datos académicos, comunicaciones y liquidaciones de honorarios. La impersonación (soporte o ADMIN operando como otro usuario) agrega urgencia: las acciones bajo suplantación deben atribuirse al actor real, no al impersonado.

## What Changes

- Nuevo modelo `AuditLog` (E-AUD) append-only con campos: actor, impersonado, materia, accion, detalle JSON, filas_afectadas, ip, user_agent, fecha_hora
- Enforce append-only a nivel DB (trigger/rule que rechaza UPDATE y DELETE) y a nivel app (repositorio sin métodos de modificación)
- Decorador `@audit_action(codigo)` para registrar acciones significativas con código estandarizado (`CALIFICACIONES_IMPORTAR`, `PADRON_CARGAR`, `COMUNICACION_ENVIAR`, etc.)
- Soporte de impersonación: sesión distinguible, acciones atribuidas al actor real, registro automático de `IMPERSONACION_INICIAR` / `IMPERSONACION_FINALIZAR`
- Permisos: `auditoria:ver` para consultar logs, `impersonacion:usar` para iniciar impersonación
- Migración 003: tabla `audit_log` con sus índices y trigger append-only
- Endpoint `GET /api/audit/log` con filtros por acción, actor, materia, rango de fechas y paginación

## Capabilities

### New Capabilities
- `audit-log-model`: modelo AuditLog, migración 003, enforce append-only (DB + app)
- `action-logging`: decorador/servicio de auditoría para registrar acciones con código estandarizado
- `impersonation`: sesión de impersonación distinguible, permisos, registro automático en audit log

### Modified Capabilities
<!-- No existing specs are modified; this is a new module. -->

## Impact

- **Backend**: nuevo modelo SQLAlchemy `AuditLog`, repositorio `AuditLogRepository`, servicio `AuditService`, decorador `@audit_action`, migración Alembic 003, endpoint `GET /api/audit/log`, integración con middleware de impersonación
- **Base de datos**: tabla `audit_log` con índices por `(tenant_id, fecha_hora)`, `(actor_id)`, `(accion)`; trigger/rule append-only que rechaza UPDATE y DELETE
- **Auth/Permisos**: nuevos permisos `auditoria:ver` e `impersonacion:usar`; seed en migración de roles
- **Dependencias**: requiere C-04 (RBAC) completado — los permisos `auditoria:ver` e `impersonacion:usar` deben existir en el sistema de roles
