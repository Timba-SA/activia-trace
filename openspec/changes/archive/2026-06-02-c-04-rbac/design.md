## Context

C-03 provides JWT authentication with `get_current_user` returning `CurrentUser` (id, tenant_id, email, roles, is_active). The JWT carries `roles: list[str]` claims (e.g., `["admin"]`, `["profesor", "coordinador"]`). However, there is no server-side permission enforcement — every authenticated user can access any endpoint. The KB defines 7 roles (ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS) with a matrix of `modulo:accion` capabilities.

This design implements the permission layer that sits between auth and every protected endpoint.

## Goals / Non-Goals

**Goals:**
- `Role` entity with name, description, permissions list, `is_system_role` flag, tenant-scoped
- `UsuarioRole` junction table for many-to-many user–role assignment
- Permission matcher service that computes effective permissions via set union across a user's roles
- `require_permission("modulo:accion")` FastAPI dependency that raises `HTTPException 403` if the user lacks the required permission
- `CurrentUser` augmented with `permissions: frozenset[str]` pre-computed at dependency resolution time
- Alembic migration 003 creating `role` and `usuario_role` tables
- Seed data for all 7 system roles with full permission matrix from `knowledge-base/03_actores_y_roles.md`
- Admin CRUD endpoints for role management and user-role assignment

**Non-Goals:**
- Temporal vigencia of role assignments → C-07 (Asignacion model)
- Impersonation → C-05 (audit-log)
- Frontend route guards → C-21 (frontend-shell-y-auth)
- Permission caching or distributed resolution (resolved server-side per request)

## Decisions

### D1 — Permission storage: list of strings on Role vs. separate Permiso + RolPermiso tables

**Decision**: Store permissions as a `JSONB` list on the `Role` model. No separate `Permiso` or `RolPermiso` tables.

**Why**: The KB says the matrix should be "administrable, not hardcoded." A flat list on Role achieves this — permissions can be added/removed per role without code changes. A full normalized schema (Permiso + RolPermiso) would add join complexity and overhead for what is fundamentally a set of strings. The permission catalog is bounded (~40 unique permissions) and roles have ~5-15 each. JSONB is well-suited for this in PostgreSQL.

**Alternatives considered**: Normalized `Permiso` + `RolPermiso` tables — rejected because it adds migration overhead, more join queries, and administrative complexity without meaningful benefit for a bounded set of string identifiers.

### D2 — require_permission layering

**Decision**: `require_permission(permission: str)` is a factory function that returns a FastAPI dependency. It calls `get_current_user` (via `Depends`), then checks `permission in current_user.permissions`. If denied, raises `HTTPException(403)`.

```python
def require_permission(permission: str):
    async def _check(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if permission not in current_user.permissions:
            raise HTTPException(status_code=403, detail="Forbidden")
        return current_user
    return _check
```

**Why**: Reuses the existing `get_current_user` so we don't duplicate JWT parsing or DB lookups. The `CurrentUser.permissions` is pre-computed so the check is a simple `in` operation — no DB query at guard time.

### D3 — Permission resolution: at dependency time, not in JWT

**Decision**: Permissions are resolved server-side during `get_current_user` by loading the user's roles from the `UsuarioRole` junction and computing the set union of their permissions. The resolved set is stored in `CurrentUser.permissions`. Permissions are NOT stored in the JWT.

**Why**: JWT is short-lived (15 min), but if a user's roles change (e.g., permissions revoked), the JWT should not carry stale permissions. Server-side resolution on every request ensures the check uses the latest data. The roles (not permissions) in the JWT are sufficient for audit logging and display purposes.

**Trade-off**: One extra DB query per authenticated request to resolve roles → acceptable for MVP. Can be optimized with caching later (Redis).

### D4 — Role-tenant relationship

**Decision**: System roles (ALUMNO, ADMIN, etc.) are created as tenant-scoped records during seed migration. Each tenant gets its own copy of the 7 system roles. Tenant administrators can modify permissions on non-system roles.

**Why**: Multi-tenant isolation requires that each tenant can independently customize role permissions. System roles (`is_system_role=True`) are protected from deletion but not from permission modification (future feature). The Repository pattern auto-scopes by `tenant_id`, so role queries are naturally isolated.

### D5 — Admin CRUD endpoints for role management

**Decision**: Provide `GET /api/roles` (list), `GET /api/roles/{id}` (get), `POST /api/roles` (create), `PUT /api/roles/{id}` (update), `DELETE /api/roles/{id}` (soft delete). System roles (`is_system_role=True`) cannot be deleted. User-role assignment via `POST /api/users/{user_id}/roles` and `DELETE /api/users/{user_id}/roles/{role_id}`.

**Why**: Role management is an admin function. Having CRUD endpoints supports the administrative UI (C-23) and keeps the permission catalog manageable without direct DB access.

### D6 — Migration 003: single migration for all RBAC structures

**Decision**: One Alembic migration (`003_rbac`) creates `role` and `usuario_role` tables, indexes, and seeds the 7 system roles with their full permission matrix.

**Why**: All RBAC entities are created together and the seed data defines the initial state. Splitting would leave the system in a partially functional state.

## Risks / Trade-offs

- **DB query per request for permission resolution** → Acceptable for MVP (<10ms on modern PG). Mitigated by using `CurrentUser.permissions` pre-computed at auth time. Future: cache in Redis.
- **JSONB permissions are not referentially integrity-checked** → Strings like `usuarios:list` could be entered incorrectly. Mitigation: use a canonical list of known permissions as a reference constant, validated at the service layer.
- **Role CRUD without vigencia means permissions are immediately effective** → Temporal allocation comes in C-07 (Asignacion). Until then, role assignment is instantaneous. Acceptable gap.
- **Admin CRUD endpoints for roles are high-governance** → All endpoints use `require_permission("roles:gestionar")`. Only ADMIN role has this permission in seed data.
