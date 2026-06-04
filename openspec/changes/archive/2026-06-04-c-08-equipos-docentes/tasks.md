## 1. Permission seed

- [x] 1.1 Add `equipos:asignar` and `equipos:ver` to permission registry
- [x] 1.2 Seed `equipos:asignar` into COORDINADOR and ADMIN roles
- [x] 1.3 Seed `equipos:ver` into PROFESOR, TUTOR, NEXO, COORDINADOR, and ADMIN roles

## 2. Repository layer — new query methods

- [x] 2.1 Add `list_with_filters(filters, usuario_id, tenant_id)` to AsignacionRepository — supports filters: materia_id, carrera_id, cohorte_id, rol, usuario_id, nombre, responsable_id, estado
- [x] 2.2 Add `bulk_create(entries: list[dict])` — creates multiple asignaciones in one session, no commit per item
- [x] 2.3 Add `list_by_team_scope(materia_id, carrera_id, cohorte_id, tenant_id)` — returns all assignments for a team scope
- [x] 2.4 Add `update_vigencia_by_team(materia_id, carrera_id, cohorte_id, fecha_inicio, fecha_fin, tenant_id)` — single UPDATE matching team scope

## 3. Schemas — new request/response models

- [x] 3.1 Add `AsignacionMasivaRequest` with `usuario_ids: list[UUID]`, `materia_id`, `carrera_id`, `cohorte_id`, `rol`, `responsable_id` (optional), `fecha_inicio`, `fecha_fin`, `comisiones` (optional)
- [x] 3.2 Add `CloneRequest` with `materia_id`, `carrera_id`, `cohorte_origen_id`, `cohorte_destino_id`, `fecha_inicio`, `fecha_fin`
- [x] 3.3 Add `VigenciaUpdateRequest` with `materia_id`, `carrera_id`, `cohorte_id`, `fecha_inicio`, `fecha_fin`
- [x] 3.4 Add `AsignacionDocenteResponse` (incluye nombre/apellido del docente)
- [x] 3.5 Add `BulkOperationResponse` with `creadas: int` (for bulk/clone) or `afectadas: int` (for vigencia update)

## 4. Service layer — new operations

- [x] 4.1 Implement `mis_equipos(usuario_id, estado, materia_id, rol, carrera_id, cohorte_id, limit, offset)` — returns filtered assignments for the authenticated user
- [x] 4.2 Implement `list_equipos(materia_id, carrera_id, cohorte_id, usuario_id, nombre, rol, responsable_id, limit, offset)` — returns filtered assignments with join to Usuario for nombre search
- [x] 4.3 Implement `asignacion_masiva(body: AsignacionMasivaRequest)` — validate all usuarios exist (single IN query), validate FKs, bulk create
- [x] 4.4 Implement `clonar(body: CloneRequest)` — read source assignments, validate dest cohorte exists, create copies with new cohorte_id and dates
- [x] 4.5 Implement `update_vigencia_equipo(body: VigenciaUpdateRequest)` — update all assignments matching scope
- [x] 4.6 Implement `exportar_equipo(materia_id, carrera_id, cohorte_id)` — query join Asignacion+Usuario, generate CSV rows

## 5. Router — `/api/equipos`

- [x] 5.1 Create `backend/app/api/v1/routers/equipos.py` with prefix `/api/equipos` and tag `equipos`
- [x] 5.2 Implement `GET /mis-equipos` — guarded by `equipos:ver`, delegates to `AsignacionService.mis_equipos`
- [x] 5.3 Implement `GET /` — guarded by `equipos:ver`, delegates to `AsignacionService.list_equipos`
- [x] 5.4 Implement `POST /asignacion-masiva` — guarded by `equipos:asignar`, delegates to `AsignacionService.asignacion_masiva`
- [x] 5.5 Implement `POST /clonar` — guarded by `equipos:asignar`, delegates to `AsignacionService.clonar`
- [x] 5.6 Implement `PATCH /vigencia` — guarded by `equipos:asignar`, delegates to `AsignacionService.update_vigencia_equipo`
- [x] 5.7 Implement `GET /exportar` — guarded by `equipos:ver`, returns StreamingResponse CSV with Content-Disposition

## 6. Wiring

- [x] 6.1 Register `equipos_router` in `backend/app/main.py`
- [x] 6.2 Run `alembic autogenerate` to verify no new migration is needed (no schema change) — NOTE: pre-existing issue in migration 008 blocks alembic; verified manually — no schema changes in 010

## 7. Tests

- [x] 7.1 Test `GET /api/equipos/mis-equipos` — happy path, all filters, empty results, 403 without permission
- [x] 7.2 Test `GET /api/equipos` — full list, filtered by materia/carrera/nombre, pagination, tenant isolation
- [x] 7.3 Test `POST /api/equipos/asignacion-masiva` — success, rollback on invalid usuario_id, optional responsable_id
- [x] 7.4 Test `POST /api/equipos/clonar` — success with N copies, empty source, invalid destino cohorte
- [x] 7.5 Test `PATCH /api/equipos/vigencia` — success with affected count, empty scope, 403 without permission
- [x] 7.6 Test `GET /api/equipos/exportar` — CSV content format, empty result with header only, streaming
