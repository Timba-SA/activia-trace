## Why

The platform needs a canonical academic structure — carreras, cohortes, and materias — as the foundation for all downstream modules: equipo docente (C-07), calificaciones (C-13), encuentros, comunicaciones, and liquidaciones. Without these entities, every module operates in a vacuum with no shared concept of what a "materia" or "cohorte" means. This change establishes the tenant-scoped catalog that every other module references by FK.

## What Changes

- **New `carrera` table**: codigo (unique per tenant), nombre, descripcion, duracion_anios, is_active
- **New `cohorte` table**: FK → carrera, nombre (unique per tenant + carrera), anio, is_active
- **New `materia` table**: FK → carrera (nullable), codigo (unique per tenant), nombre, descripcion, carga_horaria, is_active
- **Soft delete** on all three tables
- **Alembic migration 004** creating all three tables with unique constraints and FKs
- **ABM endpoints** under `/api/admin/carreras`, `/api/admin/cohortes`, `/api/admin/materias` guarded by `require_permission("estructura:gestionar")`
- **Business rule**: inactive carrera cannot have active cohorts
- **Business rule**: cannot delete carrera with existing cohorts (soft delete check)
- **Uniqueness rules**: `(tenant_id, codigo)` on Carrera and Materia; `(tenant_id, carrera_id, nombre)` on Cohorte

## Capabilities

### New Capabilities
- `estructura-academica`: CRUD for carreras, cohortes, and materias with tenant isolation, uniqueness constraints, active/inactive state management, and FK relationships

### Modified Capabilities
- *(none — first domain module in the platform)*

## Impact

- **Backend**: 3 new models, 3 new schemas (create/update/response for each), 3 new repositories, 3 new routers, Alembic migration 004
- **Permission seed**: `estructura:gestionar` already exists in the ADMIN role seed from C-04 — no seed change needed
- **Architecture**: first domain entity group; establishes the pattern all future modules will follow
