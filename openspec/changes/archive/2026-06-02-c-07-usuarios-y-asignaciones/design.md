## Context

The system has a minimal Usuario (id, tenant_id, email, hashed_password, is_active, is_2fa_enabled, totp_secret) from C-03, used only for auth. Academic operations require rich profiles (name, DNI, CUIL for payroll, CBU for payments, legajo for institutional tracking) and the ability to assign users to carrera/materia/cohorte contexts with domain roles (ALUMNO, PROFESOR, TUTOR, COORDINADOR, ADMIN, NEXO, FINANZAS). The Asignacion entity (E5 from KB) is the central authorization model — it links user + role + academic context + temporal validity.

PII attributes (DNI, CUIL, CBU) must be encrypted at rest per security requirements. Existing `encrypt_value`/`decrypt_value` from `core/security.py` (AES-256-GCM) is already proven via C-02 tenant secrets.

## Goals / Non-Goals

**Goals:**
- Expand Usuario model with all PII/profile fields (nombre, apellido, dni, cuil, telefono, direccion, fecha_nacimiento, legajo, cbu)
- Encrypt DNI, CUIL, CBU at rest using existing AES-256-GCM
- Create Asignacion model linking user + rol + carrera/materia/cohorte + temporal validity + responsable
- Provide admin CRUD endpoints for usuarios (list with filters, detail, update) and asignaciones (full CRUD)
- Add `usuarios:asignar` and `usuarios:ver-pii` permissions to ADMIN and COORDINADOR seed roles
- Migration 005: ALTER usuario + CREATE asignacion + unique index on `(tenant_id, legajo)`

**Non-Goals:**
- Assignment-based permission resolution in `get_current_user` (deferred — C-07 creates model + CRUD only)
- User creation endpoint (invitation/registration flow deferred to a future change; users are typically created via tenant seed or import)
- User deletion (soft-delete via existing `BaseRepository.soft_delete` is sufficient)
- Bulk operations or CSV import
- PA-22 (Plus keys mapping) and PA-23 (Plus accumulation) — these affect only the liquidations module (C-18)

## Decisions

### D1: Two response schemas for PII (UsuarioResponse vs UsuarioDetalleResponse)

**Decision:** Expose two schemas: `UsuarioResponse` (safe, no encrypted fields) for list views and `UsuarioDetalleResponse` (includes decrypted DNI, CUIL, CBU) for detail view, guarded by `usuarios:ver-pii`.

**Rationale:** List views (e.g. dropdown, search) should not expose PII even accidentally. The safe schema always returns DNI/CUIL/CBU as None. The detail schema decrypts in the service layer only when the caller has `usuarios:ver-pii`. This prevents PII from appearing in logs, responses, or being exposed via the list endpoint.

**Alternative considered:** Single schema with conditional nulling in the service. Rejected because it couples the schema shape to authorization logic, making it harder to audit and test. Two schemas make the contract explicit at the API boundary.

### D2: Encryption at ORM level (column stores ciphertext)

**Decision:** PII columns (`dni`, `cuil`, `cbu`) store encrypted text directly in the database. Encryption/decryption happens in the service layer, not at the ORM level (no custom type decorator).

**Rationale:** Keeping the ORM model simple avoids coupling the model to encryption logic. The service layer calls `encrypt_value` on write and `decrypt_value` on read (when authorized). This matches the pattern used for tenant secrets (C-02). The encrypted value is a stable base64 string — no indexing concern since these fields are never filtered by value.

### D3: Asignacion uses strings for role (maps to domain roles)

**Decision:** The `rol` field on Asignacion is a String, not a FK to Role. The role value corresponds to domain role names from C-04's RBAC system (ALUMNO, PROFESOR, TUTOR, COORDINADOR, NEXO, ADMIN, FINANZAS).

**Rationale:** A FK to Role would couple assignment-based roles to the system_role seed data, making it impossible to have tenant-specific role names. The string value is resolved at the permission-checking layer (future implementation). This also matches the KB definition (E5: `rol: enum`).

### D4: Asignacion nullable foreign keys for flexible contexts

**Decision:** `carrera_id`, `materia_id`, `cohorte_id` are all nullable. A user can be assigned at any level — e.g., ADMIN is typically tenant-wide (all nulls), a COORDINADOR may be assigned to a carrera but not a specific materia.

**Rationale:** The KB describes Asignacion as linking user + rol + "contexto académico concreto". Not every role needs every dimension of context. Nullable FKs give maximum flexibility. The `comisiones` field (JSONB list) provides further granularity within a materia.

### D5: Temporal validity via fecha_inicio / fecha_fin

**Decision:** `fecha_inicio` (required, default today) and `fecha_fin` (nullable, null = open-ended). No computed state_vigencia column — it's derived.

**Rationale:** Matches KB E5 model (`desde` / `hasta`). Keeping `fecha_fin` nullable allows open-ended assignments. The derived state (Vigente/Vencida) is computed at query time when needed, avoiding stale computed columns.

### D6: responsable_id nullable FK to Usuario for hierarchy

**Decision:** `responsable_id` is a nullable FK to `usuario.id` modeling the supervision chain (e.g., a profesor reports to a coordinador).

**Rationale:** Required by the KB (E5: "a quién rinde cuentas el asignado"). Self-referential FK is clean and avoids a separate hierarchy table. Nullable for top-level assignments (e.g., ADMIN reports to no one).

### D7: Migration 005 combines ALTER + CREATE in one migration

**Decision:** Single migration 005: ALTER TABLE usuario (add PII columns) + CREATE TABLE asignacion.

**Rationale:** Both changes are part of the same change (C-07). They are structurally related (asignacion references usuario). Combining them into one migration keeps the schema atomic per change.

## Risks / Trade-offs

- **[Schema coupling]** `Asignacion.rol` as a string is flexible but creates a code-level dependency on domain role names. If role names change, all existing Asignacion records with the old name become orphaned. → Mitigation: domain role names are stable (defined in KB), and any renaming will require a data migration.
- **[PII in logs]** If a developer accidentally logs a UsuarioResponse that includes PII, encrypted fields could leak ciphertext. → Mitigation: DNI/CUIL/CBU are never in `UsuarioResponse` (safe schema). Encryption makes the value unreadable even if leaked. Audit all log statements in review.
- **[Performance]** Decrypting PII on every detail request is negligible (AES-256-GCM is sub-millisecond for small fields), but if a list endpoint were to return PII for 100 users it would add latency. → Mitigation: list endpoint uses safe schema only — no decryption. Detail endpoint decrypts a single record only.
- **[Auth unchanged]** `get_current_user` does a `SELECT *` on usuario. New PII columns are returned as encrypted ciphertext blobs. This is fine — auth only reads email/hashed_password, the extra columns are ignored. → No mitigation needed.
- **[PA-22/PA-23 unrelated]** These open questions affect only the liquidations module (C-18). They do not block C-07. Marked explicitly as non-goals.

## Migration Plan

1. Code: Usuario model expansion (add PII columns)
2. Code: Asignacion model (new file)
3. Code: PII encryption helpers in service layer
4. Code: Schemas (UsuarioResponse, UsuarioDetalleResponse, AsignacionResponse, etc.)
5. Code: Repositories (UsuarioRepository, AsignacionRepository)
6. Code: Services (UsuarioService, AsignacionService)
7. Code: Routers (usuarios.py, asignaciones.py)
8. Migration: Generate 005_usuarios_asignaciones.py via Alembic autogenerate
9. Test: Unit + integration tests per spec scenarios
10. Seed: Update migration 005 RBAC seed to add new permissions

**Rollback:** `alembic downgrade -1` drops asignacion table and removes PII columns from usuario (data loss — encrypted fields cannot be recovered).

## Open Questions

- None — all design decisions are resolved for this change scope.
