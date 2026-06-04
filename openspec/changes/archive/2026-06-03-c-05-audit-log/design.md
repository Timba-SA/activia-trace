## Context

activia-trace requiere un audit log append-only para trazabilidad regulatoria y operativa. Actualmente no existe ningún registro centralizado de acciones. C-04 (RBAC) ya completó el sistema de roles y permisos, pero los permisos `auditoria:ver` e `impersonacion:usar` deben añadirse al seed de roles. Este módulo es el primero del roadmap en implementar la filosofía "todo audita" del producto.

## Goals / Non-Goals

**Goals:**
- Modelo `AuditLog` inmutable (sin UPDATE ni DELETE a nivel DB y app)
- Decorador `@audit_action` para registrar acciones con código estandarizado
- Sesión de impersonación distinguible, atribución al actor real
- Permisos `auditoria:ver` e `impersonacion:usar` integrados con C-04
- Endpoint `GET /api/audit/log` para consulta paginada con filtros
- Migración Alembic 003 con trigger append-only en PostgreSQL

**Non-Goals:**
- No se implementan alertas ni notificaciones sobre eventos de auditoría
- No se implementa rotación/archivado de logs (retención ilimitada por ahora)
- No se auditan lecturas (GET) — solo acciones de escritura significativas
- No se expone UI de auditoría (solo API)

## Decisions

### 1. Append-only enforcement at DB level via PostgreSQL trigger
- **Decisión**: Usar un trigger `BEFORE UPDATE` y `BEFORE DELETE` en la tabla `audit_log` que lanza `EXCEPTION` para rechazar modos de modificación.
- **Por qué**: La doble capa (DB + app) es estándar de seguridad — si un bug en la app intenta modificar, la DB lo bloquea igual. PostgreSQL triggers no tienen overhead significativo en una tabla append-only.
- **Alternativa considerada**: Solo enforce a nivel app → rechazada porque un error de código o acceso directo a DB podría corromper el log.

### 2. Decorator pattern for action logging
- **Decisión**: Decorador `@audit_action("CODIGO")` aplicable a métodos de servicios, que extrae actor, tenant, IP y user_agent del contexto de request (inyectado vía dependencia FastAPI), ejecuta el método, y registra el resultado con filas afectadas.
- **Por qué**: Es el approach menos invasivo — no requiere cambiar la firma de los servicios existentes. El decorador resuelve el contexto de auditoría desde una dependencia async (`AuditContext`) en lugar de desde la request directamente, respetando Clean Architecture (los servicios no conocen HTTP).
- **Alternativa considerada**: Middleware genérico que intercepta endpoints → rechazado porque no puede capturar filas afectadas ni contexto de negocio específico.

### 3. Impersonation as a session flag
- **Decisión**: El JWT de impersonación incluye un claim `impersonating_user_id` adicional al `user_id` estándar. El middleware de autenticación verifica el permiso `impersonacion:usar` al emitir tokens de impersonación. El `AuditContext` siempre expone `actor_id` (quien ejecuta) y `impersonated_user_id` (opcional).
- **Por qué**: Usar el claim del JWT evita tocar la sesión en base de datos y hace la distinción transparente para el resto del sistema. El `AuditService` usa siempre `actor_id` del token, no el `user_id` impersonado.
- **Alternativa considerada**: Tabla separada de sesiones de impersonación → rechazada por complejidad innecesaria; el JWT ya contiene toda la información necesaria.

### 4. Códigos de acción como constantes
- **Decisión**: Los códigos de acción (`CALIFICACIONES_IMPORTAR`, `PADRON_CARGAR`, etc.) se definen como constantes en una clase/enum `AuditActionCode` en `modules/audit/constants.py`.
- **Por qué**: Tipado seguro, autocompletado, y un solo lugar para mantener el catálogo de códigos.

### 5. Seed de permisos en migración existente de roles
- **Decisión**: Agregar `auditoria:ver` e `impersonacion:usar` al seed de roles existente (migración que crea roles por defecto de C-04), no crear una migración separada para permisos.
- **Por qué**: Ya existe el mecanismo de seed de roles. Extenderlo evita migraciones huérfanas. Los permisos se asignan según la matriz de `03_actores_y_roles.md` §3.3: `auditoria:ver` para COORDINADOR, ADMIN, FINANZAS; `impersonacion:usar` para ADMIN.

## Risks / Trade-offs

- **Tamaño de la tabla audit_log**: al ser append-only sin rotación, la tabla crece indefinidamente → mitigación inicial: índices adecuados por `(tenant_id, fecha_hora)`; en el futuro se puede implementar particionado por mes o archivado a almacenamiento frío.
- **Overhead del decorador**: cada acción auditada agrega una escritura síncrona en la misma transacción → mitigación: el decorador es opt-in (solo acciones significativas), y en el futuro se puede migrar a escritura asíncrona si el throughput lo requiere.
- **Trigger de DB**: puede ser invisible para developers que no revisen migraciones → mitigación: documentar el trigger en el comentario de la migración y en el modelo.
