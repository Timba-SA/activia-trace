## Why

C-03 established authentication (JWT, 2FA, password recovery) and provides `get_current_user` with a `CurrentUser` carrying `roles: list[str]`. However, there is no mechanism to enforce **what each role can do**. Every authenticated user currently has full access to all endpoints. This change introduces fine-grained RBAC with `modulo:accion` permissions so endpoints can declare required permissions and reject unauthorized requests with 403 before any business logic executes.

## What Changes

- **New `Role` entity**: name, description, list of permissions, `is_system_role` flag, tenant-scoped
- **New `UsuarioRole` junction table**: many-to-many between `Usuario` and `Role` with tenant scope
- **Permission model**: `modulo:accion` string-based permissions stored as a list on each role
- **Permission matcher service**: resolves effective permissions from a user's roles via set union
- **`require_permission` FastAPI dependency**: layered on top of `get_current_user`, checks `modulo:accion`, returns 403 if denied
- **`CurrentUser` augmentation**: add `permissions: set[str]` pre-computed from resolved roles
- **Seed data migration**: 7 system roles (ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS) with their full permission matrix from the KB
- **Alembic migration 003**: creates `role` and `usuario_role` tables with seed data

## Capabilities

### New Capabilities
- `rbac`: Role-based access control — role CRUD, user-role assignment, permission matching, and the `require_permission` FastAPI guard dependency

### Modified Capabilities
- `auth`: The `CurrentUser` schema gains a `permissions` field; the `get_current_user` dependency now resolves and injects effective permissions. JWT `roles` claim remains unchanged; permissions are resolved server-side.

## Impact

- **Backend**: New models (`Role`, `UsuarioRole`), repository, service, schemas, router (admin CRUD), FastAPI dependency (`require_permission`), seed data in migration
- **Auth**: `CurrentUser` schema gets `permissions: frozenset[str]` field
- **Dependencies**: `C-03` (get_current_user, JWT roles claims)
- **Database**: Migration 003 creating two tables
- **Tests**: Permission matching unit tests, role CRUD, user-role assignment, `require_permission` on endpoint (both authorized and unauthorized)
