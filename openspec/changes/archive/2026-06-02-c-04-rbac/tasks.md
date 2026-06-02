## 1. Models and Schemas

- [x] 1.1 Create `Role` model with fields: id, tenant_id, name (unique per tenant), description, permissions (JSONB), is_system_role, timestamps, soft delete
- [x] 1.2 Create `UsuarioRole` junction model with composite PK (usuario_id, role_id) and tenant_id
- [x] 1.3 Add `roles` relationship to existing `Usuario` model
- [x] 1.4 Create Pydantic schemas: `RoleCreate`, `RoleUpdate`, `RoleResponse`, `RoleListResponse`, `UserRoleAssignRequest`, `UserRoleResponse`

## 2. Repositories

- [x] 2.1 Create `RoleRepository` extending BaseRepository with methods: list, get_by_name, get_by_user_id
- [x] 2.2 Create `UsuarioRoleRepository` with methods: assign_role, remove_role, get_user_roles

## 3. Permission Matcher Service

- [x] 3.1 Create `PermissionService` with `resolve_user_permissions(user_id) -> set[str]` that loads roles from `UsuarioRole`, computes union of permissions
- [x] 3.2 Create `has_permission(permissions: set[str], required: str) -> bool` utility function

## 4. FastAPI Dependency Guard

- [x] 4.1 Create `require_permission(permission: str)` factory function in `core/dependencies.py`
- [x] 4.2 Augment `get_current_user` to resolve and inject `permissions: frozenset[str]` into `CurrentUser`
- [x] 4.3 Update `CurrentUser` schema to include `permissions: frozenset[str]`

## 5. Admin CRUD Endpoints

- [x] 5.1 Create `api/v1/routers/roles.py` with: GET `/api/roles` (list), GET `/api/roles/{id}` (get), POST `/api/roles` (create), PUT `/api/roles/{id}` (update), DELETE `/api/roles/{id}` (soft delete, forbid system roles)
- [x] 5.2 Create `api/v1/routers/user_roles.py` with: GET `/api/users/{user_id}/roles`, POST `/api/users/{user_id}/roles`, DELETE `/api/users/{user_id}/roles/{role_id}`
- [x] 5.3 Register both routers in `app/main.py` with prefix `/api` and `require_permission("roles:gestionar")` guard

## 6. Alembic Migration and Seed Data

- [x] 6.1 Generate Alembic migration `003_rbac` creating `role` and `usuario_role` tables
- [x] 6.2 Define canonical permission set constant (`PERMISSION_CATALOG`) covering all modulo:accion from the KB matrix
- [x] 6.3 Add seed data function that creates 7 system roles (ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS) with full permission matrix per tenant

## 7. Tests

- [x] 7.1 Unit tests for `PermissionService.has_permission` — single role, union of roles, missing permission, empty roles
- [x] 7.2 Integration tests for role CRUD — create, list, get, update, soft delete, delete system role forbidden, duplicate name
- [x] 7.3 Integration tests for user-role assignment — assign, remove, get, tenant isolation
- [x] 7.4 Integration tests for `require_permission` — authorized passes, unauthorized returns 403, unauthenticated returns 401
- [x] 7.5 Integration tests for permission resolution in `get_current_user` — single role permissions, union across multiple roles
