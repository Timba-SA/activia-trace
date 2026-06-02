## ADDED Requirements

### Requirement: Role model

The system SHALL provide a `Role` entity with fields: `id` (UUID PK), `tenant_id` (UUID FK), `name` (string, unique per tenant), `description` (string, nullable), `permissions` (JSONB list of `modulo:accion` strings), `is_system_role` (boolean, default False), standard timestamps and soft delete from BaseModelMixin.

#### Scenario: Create role

- **WHEN** an authenticated user with `roles:gestionar` permission sends a POST request to `/api/roles` with a valid `name` and `permissions` list
- **THEN** the system SHALL create a new role and return it with status `201`

#### Scenario: Create role with duplicate name

- **WHEN** a POST request to `/api/roles` includes a `name` that already exists for the current tenant
- **THEN** the system SHALL return `409 Conflict`

#### Scenario: List roles

- **WHEN** a GET request is sent to `/api/roles`
- **THEN** the system SHALL return all roles for the current tenant (excluding soft-deleted), with pagination support

#### Scenario: Get role by id

- **WHEN** a GET request is sent to `/api/roles/{id}` with a valid role id
- **THEN** the system SHALL return the role with its permissions

#### Scenario: Update role permissions

- **WHEN** a PUT request is sent to `/api/roles/{id}` with a new `permissions` list
- **THEN** the system SHALL update the role's permissions and return the updated role

#### Scenario: Delete non-system role

- **WHEN** a DELETE request is sent to `/api/roles/{id}` for a role with `is_system_role = False`
- **THEN** the system SHALL soft-delete the role and return `204`

#### Scenario: Delete system role is forbidden

- **WHEN** a DELETE request is sent to `/api/roles/{id}` for a role with `is_system_role = True`
- **THEN** the system SHALL return `403 Forbidden`

### Requirement: User-role assignment

The system SHALL provide a `usuario_role` junction table (usuario_id UUID FK, role_id UUID FK, tenant_id UUID FK, PK = (usuario_id, role_id)). Users can have multiple roles and roles can be assigned to multiple users.

#### Scenario: Assign role to user

- **WHEN** a POST request is sent to `/api/users/{user_id}/roles` with a valid `role_id`
- **THEN** the system SHALL assign the role to the user and return `201`

#### Scenario: Remove role from user

- **WHEN** a DELETE request is sent to `/api/users/{user_id}/roles/{role_id}` for an active assignment
- **THEN** the system SHALL remove the role assignment and return `204`

#### Scenario: Get user roles

- **WHEN** a GET request is sent to `/api/users/{user_id}/roles`
- **THEN** the system SHALL return all roles assigned to that user

#### Scenario: Roles are tenant-isolated

- **WHEN** a user from tenant A is assigned a role from tenant B
- **THEN** the system SHALL return `404 Not Found`

### Requirement: Permission matching

The system SHALL provide a permission matcher that, given a set of role permissions and a required `modulo:accion` string, returns whether the user has the permission. Permission checks SHALL be case-sensitive exact matches.

#### Scenario: User has permission via single role

- **WHEN** a user has a single role with permissions `["usuarios:list", "usuarios:create"]` and the required permission is `usuarios:list`
- **THEN** the matcher SHALL return `True`

#### Scenario: User has permission via union of multiple roles

- **WHEN** a user has roles with permissions `["usuarios:list"]` and `["usuarios:create"]` respectively, and the required permission is `usuarios:create`
- **THEN** the matcher SHALL return `True`

#### Scenario: User does not have permission

- **WHEN** a user's roles do not contain the required `modulo:accion` in any of their permission sets
- **THEN** the matcher SHALL return `False`

### Requirement: require_permission FastAPI dependency

The system SHALL provide a `require_permission(permission: str)` factory that returns a FastAPI dependency. The dependency SHALL call `get_current_user`, inspect `current_user.permissions`, and raise `HTTPException 403` with `detail="Forbidden"` if the required permission is not present.

#### Scenario: Authorized request passes guard

- **WHEN** a request includes a valid JWT for a user whose permissions contain the required `modulo:accion`
- **THEN** the dependency SHALL return the `CurrentUser` and the request SHALL proceed to the endpoint handler

#### Scenario: Unauthorized request returns 403

- **WHEN** a request includes a valid JWT for a user whose permissions do NOT contain the required `modulo:accion`
- **THEN** the dependency SHALL raise `HTTPException 403`

#### Scenario: Unauthenticated request is caught before require_permission

- **WHEN** a request lacks a valid JWT
- **THEN** `get_current_user` SHALL raise `HTTPException 401` before `require_permission` is evaluated

### Requirement: CurrentUser includes resolved permissions

The `CurrentUser` schema SHALL include a `permissions: frozenset[str]` field. The `get_current_user` dependency SHALL resolve the user's effective permissions by loading all assigned roles (from `usuario_role` junction) and computing the set union of their `permissions` lists. This SHALL happen on every request (no caching in JWT).

#### Scenario: CurrentUser has permissions after login

- **WHEN** `get_current_user` resolves a valid token for a user with roles `[admin]` where admin has `["usuarios:list", "usuarios:create"]`
- **THEN** the returned `CurrentUser.permissions` SHALL equal `frozenset({"usuarios:list", "usuarios:create"})`

#### Scenario: User with multiple roles gets union of permissions

- **WHEN** a user has roles `profesor` (permissions: `["calificaciones:importar", "atrasados:ver"]`) and `coordinador` (permissions: `["equipos:asignar"]`)
- **THEN** the resolved `CurrentUser.permissions` SHALL equal `frozenset({"calificaciones:importar", "atrasados:ver", "equipos:asignar"})`

### Requirement: System role seed data

The system SHALL seed 7 system roles (`is_system_role = True`) for each tenant created: ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS. Each role SHALL have the permission set defined in `knowledge-base/03_actores_y_roles.md` §3.3. The seed SHALL be applied in migration 003.

#### Scenario: Seed roles are created for new tenant

- **WHEN** a new tenant is created
- **THEN** the system SHALL create all 7 system roles with their full permission matrix assigned to that tenant

#### Scenario: Seed roles cannot be deleted

- **WHEN** a delete request targets any of the 7 seed roles
- **THEN** the system SHALL return `403 Forbidden` because `is_system_role = True`
