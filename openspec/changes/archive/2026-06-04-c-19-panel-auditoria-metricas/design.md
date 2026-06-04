## Context

C-05 established the audit logging foundation: `AuditLog` model, `AuditLogRepository` (append-only, `find()` with filters and pagination), `AuditService` (programmatic logging), and the `GET /api/audit/log` endpoint guarded by `auditoria:ver`. There is currently no aggregation, metrics, or dashboard layer — ADMIN/COORDINADOR cannot visualize audit data without raw SQL.

This change adds 5 read-only endpoints that query the existing `audit_log` table plus the `comunicacion` table for communication state breakdowns. No schema changes, no new tables.

## Goals / Non-Goals

**Goals:**
- Provide 4 metric aggregation endpoints for the audit dashboard
- Provide a convenience "last N actions" endpoint (default 200)
- All endpoints tenant-scoped via existing `AuditLogRepository._apply_tenant_scope()`
- All endpoints guarded by `auditoria:ver` (already deployed)
- Reuse existing repository patterns — no new ORM abstractions

**Non-Goals:**
- No frontend/UI — this change is backend-only
- No new tables or migrations
- No changes to the existing `GET /api/audit/log` endpoint
- No RBAC seed changes (auditoria:ver is already referenced in the KB matrix and the existing router)

## Decisions

### 1. Router: New `auditoria.py` at `/api/auditoria`

- ✅ New `routers/auditoria.py` with `APIRouter(prefix="/api/auditoria", tags=["auditoria"])`
- ✅ Existing `routers/audit.py` at `/api/audit` stays untouched for backward compatibility
- **Rationale**: The `/api/audit` prefix was used for the raw log endpoint. The dashboard/metrics endpoints form a separate concern with a different semantic — they deserve their own prefix. The duplication is minimal (both use `AuditLogRepository`) and avoids confusion.

### 2. Repository: Aggregation methods on `AuditLogRepository`

- Add `count_by_day(desde, hasta, materia_id, actor_id)` — `GROUP BY DATE(fecha_hora)` with optional filters
- Add `count_by_actor(desde, hasta, materia_id)` — `GROUP BY actor_id` with optional filters
- Add `count_by_actor_materia(desde, hasta)` — `GROUP BY actor_id, materia_id`
- **Rationale**: Metrics are a read projection of the same data. Putting queries on the existing repository keeps query logic co-located with the model and avoids a separate read-model layer. Each method returns typed dicts, not ORM instances.

### 3. Communication states: Cross-repository via `AuditoriaService`

- Communication states (`Pendiente`, `En envío`, `Enviado`, `Fallido`, `Cancelado`) live on the `Comunicacion` model, not `AuditLog`
- Create `AuditoriaService` that depends on both `AuditLogRepository` and `ComunicacionRepository`
- The `/api/auditoria/metricas/comunicaciones` endpoint calls `ComunicacionRepository` for state aggregation
- **Rationale**: The `comunicacion` table has an `estado` column — a simple `GROUP BY docente_id, estado` with `COUNT(*)` is sufficient. No new model needed.

### 4. `ultimas-acciones` as a lightweight wrapper

- `GET /api/auditoria/ultimas-acciones` delegates to `AuditLogRepository.find()` with `limit` defaulting to 200 (instead of the default 20 on `/api/audit/log`)
- Same response schema as the list endpoint
- **Rationale**: Avoids duplicating filter/pagination logic. The only difference is the default limit.

### 5. Schemas: New `schemas/auditoria.py`

- `MetricaAccionesPorDia` — `fecha: date`, `cantidad: int`
- `MetricaPorDocente` — `docente_id: uuid`, `docente_nombre: str`, `total: int`, `detalle_por_accion: dict[str, int]`
- `MetricaPorMateria` — `docente_id: uuid`, `materia_id: uuid`, `materia_nombre: str`, `total: int`
- `MetricaComunicaciones` — `docente_id: uuid`, `estados: dict[str, int]` (key: estado, value: count)

## Risks / Trade-offs

- **Performance on large audit_log tables** → Metric queries use full-scan `GROUP BY` on millions of rows. Mitigation: existing composite indexes on `(tenant_id, fecha_hora)`, `(actor_id)`, `(accion)` cover most GROUP BY columns. Add a composite index on `(tenant_id, actor_id, materia_id)` if the `por-materia` query is slow.
- **Communication state endpoint crosses domain boundaries** → The auditoria module now depends on the comunicaciones repository. Mitigation: this is a read-only dependency enforced at the service layer, not a circular dependency. Acceptable for a cross-cutting dashboard module.
- **COORDINADOR scope propio** → COORDINADOR should only see metrics for their own materias. The existing `AuditLogRepository` does not filter by materia scope — that would require checking the `equipo_docente` table. Mitigation: add an optional `materias_ids` filter parameter. When the current user is COORDINADOR, the router resolves the list of materias they are assigned to and passes it to the repository.
