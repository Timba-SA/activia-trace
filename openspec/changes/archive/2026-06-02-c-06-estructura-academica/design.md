## Context

C-04 (RBAC) is complete. The platform has auth, tenant isolation, and permission guards. However, there are no domain entities yet — no concept of carrera, cohorte, or materia. Every future module (equipo docente, calificaciones, encuentros, liquidaciones) needs these as FK references. C-06 establishes the canonical academic structure catalog per tenant.

The KB defines three entities (E1 Carrera, E2 Cohorte, E3 Materia) in `04_modelo_de_datos.md`. Two open questions (PA-01, PA-07) from `10_preguntas_abiertas.md` must be resolved for this design.

## PA Resolutions

### PA-01 — Catálogo de materias (Materia vs InstanciaDictado)

**Decision**: `Materia` is the single catalog entity. There is no separate `InstanciaDictado` at this stage.

**Why**: The KB §04 defines Materia (E3) as the unique catalog per tenant — it has `codigo`, `nombre`, `estado`. The "instance per cohort" concept (e.g., "Programación – Python" vs "Programación – Java") maps to a future `AsignacionMateria` or `ProgramaMateria` entity (C-13 encuentros, C-17 programas). Materia is the catalog, not the offering.

**Open for future**: When C-17 introduces programas, the Materia entity may gain a `carrera_id` FK or a separate `OfertaMateria` entity may be created. For now, `materia.carrera_id` is nullable — some subjects may not belong to a specific career.

### PA-07 — Cohorte pertenece a Carrera

**Decision**: `Cohorte` has a mandatory FK `carrera_id`. A cohort belongs to exactly one career.

**Why**: The KB §04 entity model explicitly states `Carrera (1) ─── (N) Cohorte`. Cross-career cohorts are not supported. An alumno may be enrolled in materias from different carreras, but each cohorte is scoped to a single carrera.

## Goals / Non-Goals

**Goals:**
- Carrera, Cohorte, and Materia models with tenant isolation and soft delete
- Unique constraints: `(tenant_id, codigo)` on Carrera and Materia; `(tenant_id, carrera_id, nombre)` on Cohorte
- FK: cohorte.carrera_id → carrera.id; materia.carrera_id → carrera.id (nullable)
- Business rule: inactive carrera cannot have active cohorts (enforced at service layer)
- Business rule: cannot soft-delete carrera with non-deleted cohorts (enforced at repository/service)
- ABM endpoints under `/api/admin/carreras`, `/api/admin/cohortes`, `/api/admin/materias`
- All endpoints guarded by `require_permission("estructura:gestionar")`
- Alembic migration 004 creating all three tables
- Paginated list, get by id, create, update, soft delete for all three entities
- Tests: CRUD, uniqueness per tenant, multi-tenant isolation, active/inactive state

**Non-Goals:**
- Temporal vigencia on cohorte (vig_desde/vig_hasta) — deferred to future refinement; MVP uses is_active
- Materia linking to multiple carreras — `materia.carrera_id` is nullable, single FK
- Import from Moodle or external systems
- Frontend UI — C-21 (frontend-shell-y-auth) will handle this later
- Audit logging of CRUD operations — C-05 (audit-log) will handle this later

## Decisions

### D1 — Single `carrera_id` FK on Materia (nullable)

**Decision**: `materia.carrera_id` is a nullable FK to `carrera.id`.

**Why**: Some materias are shared across carreras (e.g., "Inglés Técnico"). Making the FK nullable allows catalog-level materias without a mandatory career binding. The KB defines Materia as the tenant-wide catalog; career association is optional metadata at this level. Career-specific binding happens through future entities (ProgramaMateria, Asignacion).

### D2 — `is_active` boolean instead of temporal vigencia

**Decision**: Use a simple `is_active: bool` column instead of `vig_desde`/`vig_hasta` date ranges.

**Why**: MVP requirement. The KB defines `estado: Activa|Inactiva` as an enum for all three entities. Temporal vigencia (vig_desde/vig_hasta on Cohorte) is documented in KB §04 but deferred — it adds complexity (date validation, overlapping ranges, derived state) with no current consumer. Can be added later via migration without breaking changes.

**Trade-off**: Cohorte will need temporal vigencia when liquidations (C-18) need to determine which cohortes are "active" for a given month. Acceptable gap for MVP.

### D3 — Nested router structure: single file per entity

**Decision**: Three separate router files (`carreras.py`, `cohortes.py`, `materias.py`) under `backend/app/api/v1/routers/`, each registered in `main.py`.

**Why**: Follows the existing project pattern (`auth.py`, `roles.py`, `user_roles.py`). Each router file < 200 LOC. Endpoints are on `/api/admin/carreras`, `/api/admin/cohortes`, `/api/admin/materias` — the `admin/` segment groups them under the `estructura:gestionar` permission scope.

### D4 — Service layer for business rules

**Decision**: Business rules (inactive carrera cannot have active cohorts, cascade protection on delete) live in a dedicated `estructura_service.py` file, not in repositories or routers.

**Why**: Repositories are data-access only (following the existing `BaseRepository` pattern). Routers orchestrate HTTP concerns. The service layer holds domain logic between them. This is the first service layer in the project — C-03's `AuthService` established the pattern.

### D5 — Migration 004: single migration for all three tables

**Decision**: One Alembic migration (`004_estructura_academica`) creates `carrera`, `cohorte`, and `materia` tables with all constraints, indexes, and FKs.

**Why**: All three entities are created together as a logical unit. The migration is additive-only (creating new tables, not modifying existing ones). No rollback risk.

## Risks / Trade-offs

- **First service layer in the project** → The service pattern (`estructura_service.py`) sets a precedent. Future modules should follow the same pattern. Clear naming convention documented here.
- **`is_active` vs temporal vigencia** → Cohorte temporal vigencia will need a future migration. The `is_active` field is compatible — `vig_hasta IS NULL AND is_active = true` would be the derived state.
- **Materia without carrera** → Queries that join materia → cohorte → carrera may yield null for shared materias. Consumers must handle nullable `carrera_id` gracefully.
- **PA-01 resolution binds the model** → If future requirements demand a separate `InstanciaDictado` entity, existing `materia.carrera_id` may need migration. Acceptable risk — the single-catalog approach is the simplest starting point.
