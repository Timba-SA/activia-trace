## 1. Model Layer

- [x] 1.1 Expand Usuario model with PII columns: `nombre`, `apellido`, `dni`, `cuil`, `telefono`, `direccion`, `fecha_nacimiento`, `legajo`, `cbu` — all String where applicable (UUID FK to Usuario for `responsable_id` not on Usuario itself) (TDD: test model has columns)
- [x] 1.2 Create Asignacion model with fields: `usuario_id` (FK→usuario), `rol` (String), `carrera_id` (FK→carrera, nullable), `materia_id` (FK→materia, nullable), `cohorte_id` (FK→cohorte, nullable), `responsable_id` (FK→usuario, nullable), `fecha_inicio` (Date), `fecha_fin` (Date, nullable), `comisiones` (JSONB, default []), `is_active` (Boolean, default True), standard mixin fields (TDD: test model fields, FKs, defaults)

## 2. Schema Layer

- [x] 2.1 Create `backend/app/schemas/usuario.py` with `UsuarioUpdate`, `UsuarioResponse` (safe — no PII), `UsuarioDetalleResponse` (includes decrypted PII), `UsuarioListResponse` — all with `extra='forbid'` (TDD: test schema validation)
- [x] 2.2 Create `backend/app/schemas/asignacion.py` with `AsignacionCreate`, `AsignacionUpdate`, `AsignacionResponse`, `AsignacionListResponse` — all with `extra='forbid'` (TDD: test schema validation, required fields)

## 3. Repository Layer

- [x] 3.1 Create `backend/app/repositories/usuario_repository.py` extending `BaseRepository[Usuario]` with custom methods: `get_by_email`, `get_by_legajo`, `search_by_filters` (partial match on nombre/apellido, exact on legajo/is_active) (TDD: test repository queries against real DB)
- [x] 3.2 Create `backend/app/repositories/asignacion_repository.py` extending `BaseRepository[Asignacion]` with custom method: `list_by_usuario(usuario_id)` (TDD: test repository queries against real DB)

## 4. Service Layer

- [x] 4.1 Create `backend/app/services/usuario_service.py` with `UsuarioService`: `get`, `list` (with search/filter/pagination), `update` (with PII encryption on write), `get_detalle` (with conditional PII decryption based on `usuarios:ver-pii` permission). PII encryption via `encrypt_value()` for dni/cuil/cbu on write; decryption via `decrypt_value()` on detail read when authorized. (TDD: test PII encryption round-trip, permission-gated PII exposure, filtering, duplicate legajo rejection)
- [x] 4.2 Create `backend/app/services/asignacion_service.py` with `AsignacionService`: `create`, `get`, `list`, `update`, `soft_delete`, `list_by_usuario`. Validate FKs exist (usuario, carrera, materia, cohorte) on create. Validate responsable_id exists in same tenant. (TDD: test CRUD, FK validation, responsible hierarchy, temporal validity defaults)

## 5. Router Layer

- [x] 5.1 Create `backend/app/api/v1/routers/usuarios.py` with: `GET /api/admin/usuarios` (list with filters, guarded by `usuarios:gestionar`, returns `UsuarioListResponse`), `GET /api/admin/usuarios/{id}` (detail, guarded by `usuarios:gestionar`, checks `usuarios:ver-pii` for PII decryption, returns `UsuarioDetalleResponse`), `PUT /api/admin/usuarios/{id}` (update, guarded by `usuarios:gestionar`), `GET /api/admin/usuarios/{id}/asignaciones` (user's assignments, guarded by `usuarios:gestionar`). Follow existing carrera.py router pattern. (TDD: test endpoint responses, permission guards, 404 handling)
- [x] 5.2 Create `backend/app/api/v1/routers/asignaciones.py` with: `GET /api/admin/asignaciones` (list), `POST /api/admin/asignaciones` (create), `GET /api/admin/asignaciones/{id}` (get), `PUT /api/admin/asignaciones/{id}` (update), `DELETE /api/admin/asignaciones/{id}` (soft delete). All guarded by `usuarios:asignar`. Follow existing router pattern. (TDD: test all CRUD endpoints, permission guards, 404/403 handling)

## 6. Migration and Seed Data

- [x] 6.1 Generate migration 005 via Alembic autogenerate: ALTER TABLE usuario (add PII columns) + CREATE TABLE asignacion (all fields, FKs, JSONB comisiones) + unique index `uix_usuario_tenant_legajo` on `(tenant_id, legajo)` WHERE `deleted_at IS NULL`. (TDD: test migration up/down, verify schema after upgrade)
- [x] 6.2 Update RBAC seed in migration 005: Add `usuarios:asignar` and `usuarios:ver-pii` to ADMIN and COORDINADOR system roles. Migration must be idempotent (update existing roles, not recreate). Use UPDATE on the role JSONB permissions array. (TDD: test permissions added to both roles, test idempotency)

## 7. App Registration

- [x] 7.1 Register `usuarios` and `asignaciones` routers in `backend/app/api/v1/__init__.py` or main app (following existing pattern from carreras/cohortes/materias registration)
- [x] 7.2 Verify full integration: create tenant, seed roles, create user with PII, create asignacion, verify PII is encrypted in DB, verify list endpoint hides PII, verify detail endpoint with/without `usuarios:ver-pii`
