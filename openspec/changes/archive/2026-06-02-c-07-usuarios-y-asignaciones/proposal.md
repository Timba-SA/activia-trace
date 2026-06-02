## Why

The system currently has a minimal Usuario model (email + password + 2FA) created in C-03, sufficient only for authentication. Real academic management requires rich user profiles with PII (name, DNI, CUIL, CBU, etc.) and a model to link users to academic contexts with a role. Without these, the system cannot support team assignments (C-08), communication flows (C-09), or liquidations (C-18). This change expands Usuario with PII fields and introduces the Asignacion model — the central entity that binds users to roles within carrera/materia/cohorte contexts.

## What Changes

- **Usuario model expansion**: Add `nombre`, `apellido`, `dni` (encrypted), `cuil` (encrypted), `telefono`, `direccion`, `fecha_nacimiento`, `legajo`, `cbu` (encrypted) columns
- **Asignacion model**: New entity linking users to academic contexts with a role, temporal validity, optional responsible_id hierarchy, and JSONB comisiones list
- **PII encryption at rest**: AES-256-GCM via existing `encrypt_value`/`decrypt_value` for DNI, CUIL, CBU fields. Two response schemas: safe (no PII) and detailed (PII, requires `usuarios:ver-pii`)
- **Admin CRUD endpoints**: Usuario list/detail/update + Asignacion full CRUD + user's assignments endpoint
- **Migration 005**: ALTER TABLE usuario (PII columns) + CREATE TABLE asignacion + unique index `(tenant_id, legajo)` + FK constraints
- **RBAC seed update**: Add `usuarios:asignar` and `usuarios:ver-pii` permissions to ADMIN and COORDINADOR roles
- **Auth path unaffected**: `get_current_user` reads email/hashed_password from Usuario; PII new columns are returned as encrypted blobs transparently — no change to auth flow

## Capabilities

### New Capabilities

- `usuarios-expansion`: Usuario model expansion with PII fields, legajo (unique per tenant), AES-256-GCM encryption for DNI/CUIL/CBU, two-tier response schemas (safe / detailed with PII), and `usuarios:ver-pii` guard
- `asignaciones`: New Asignacion entity linking users to academic contexts (carrera, materia, cohorte, comisiones) with a role, temporal validity dates, optional jerarquía via responsable_id, and full CRUD endpoints

### Modified Capabilities

- `rbac`: Update ADMIN and COORDINADOR seed permission sets to include `usuarios:asignar` and `usuarios:ver-pii`

## Impact

- **Models**: `backend/app/models/usuario.py` — add PII columns. New `backend/app/models/asignacion.py`
- **Schemas**: New `backend/app/schemas/usuario.py` with `UsuarioUpdate`, `UsuarioResponse`, `UsuarioDetalleResponse`, `UsuarioListResponse`. New `backend/app/schemas/asignacion.py` with `AsignacionCreate`, `AsignacionUpdate`, `AsignacionResponse`, `AsignacionListResponse`
- **Services**: New `backend/app/services/usuario_service.py`, `backend/app/services/asignacion_service.py`
- **Repositories**: New `backend/app/repositories/usuario_repository.py`, `backend/app/repositories/asignacion_repository.py`
- **Routers**: New `backend/app/api/v1/routers/usuarios.py` and `backend/app/api/v1/routers/asignaciones.py`
- **Migration**: New `backend/alembic/versions/005_usuarios_asignaciones.py`
- **No auth path changes**: `get_current_user` unaffected — new columns are transparent encrypted blobs for auth
