## 1. Repository — Aggregation methods

- [x] 1.1 Add `count_by_day()` method to `AuditLogRepository` — `GROUP BY DATE(fecha_hora)` with optional filters (desde, hasta, materia_id, actor_id), returns list of `{fecha: date, cantidad: int}`
- [x] 1.2 Add `count_by_actor()` method to `AuditLogRepository` — `GROUP BY actor_id` with optional filters (desde, hasta, materia_id), returns list of `{actor_id, total, detalle_por_accion: dict}`
- [x] 1.3 Add `count_by_actor_materia()` method to `AuditLogRepository` — `GROUP BY actor_id, materia_id` with optional filters (desde, hasta, actor_id), returns list of `{actor_id, materia_id, total}`

## 2. Schemas — Metric response models

- [x] 2.1 Create `schemas/auditoria.py` with:
  - `MetricaAccionesPorDia(fecha: date, cantidad: int)`
  - `MetricaPorDocente(docente_id, docente_nombre, total, detalle_por_accion: dict[str, int])`
  - `MetricaPorDocenteListResponse(items: list[MetricaPorDocente])`
  - `MetricaPorMateria(docente_id, materia_id, materia_nombre, total)`
  - `MetricaPorMateriaListResponse(items: list[MetricaPorMateria])`
  - `MetricaComunicaciones(docente_id, estados: dict[str, int])`
  - `MetricaComunicacionesListResponse(items: list[MetricaComunicaciones])`

## 3. Service — AuditoriaService

- [x] 3.1 Create `services/auditoria_service.py` with `AuditoriaService` that:
  - Wraps `AuditLogRepository.count_by_day()`, `count_by_actor()`, `count_by_actor_materia()`
  - Resolves `docente_nombre` from Usuario lookup and `materia_nombre` from Materia lookup
  - Wraps `ComunicacionRepository` for communication state aggregation

## 4. Router — auditoria endpoints

- [x] 4.1 Create `routers/auditoria.py` with `APIRouter(prefix="/api/auditoria")` and all endpoints guarded by `require_permission("auditoria:ver")`:
  - `GET /metricas/acciones-por-dia` — delegates to `AuditoriaService`
  - `GET /metricas/por-docente` — delegates to `AuditoriaService`
  - `GET /metricas/por-materia` — delegates to `AuditoriaService`
  - `GET /metricas/comunicaciones` — delegates to `AuditoriaService`
  - `GET /ultimas-acciones` — delegates to `AuditLogRepository.find()` with limit default 200

- [x] 4.2 Register `routers/auditoria.py` in the app's router registration

## 5. Tests

- [x] 5.1 Write tests for `AuditLogRepository.count_by_day()` — verify GROUP BY behavior, filters, tenant scope
- [x] 5.2 Write tests for `AuditLogRepository.count_by_actor()` — verify grouping and breakdown
- [x] 5.3 Write tests for `AuditLogRepository.count_by_actor_materia()` — verify grouping by both fields
- [x] 5.4 Write integration tests for `GET /api/auditoria/ultimas-acciones` — verify default limit 200, custom limit, filters, 403 without permission
- [x] 5.5 Write integration tests for `GET /api/auditoria/metricas/acciones-por-dia` — verify date aggregation, materia filter, tenant scope, 403
- [x] 5.6 Write integration tests for `GET /api/auditoria/metricas/por-docente` — verify actor grouping, detalle_por_accion, tenant scope
- [x] 5.7 Write integration tests for `GET /api/auditoria/metricas/por-materia` — verify actor×materia grouping, tenant scope
- [x] 5.8 Write integration tests for `GET /api/auditoria/metricas/comunicaciones` — verify state breakdown, tenant scope
