## ADDED Requirements

### Requirement: Usuario model expansion with PII fields

The system SHALL expand the Usuario model to include PII and profile fields: `nombre` (string, NOT NULL), `apellido` (string, NOT NULL), `dni` (string, encrypted AES-256-GCM, nullable), `cuil` (string, encrypted AES-256-GCM, nullable), `telefono` (string, nullable), `direccion` (string, nullable), `fecha_nacimiento` (date, nullable), `legajo` (string, nullable, unique per tenant), `cbu` (string, encrypted AES-256-GCM, nullable). The fields `dni`, `cuil`, and `cbu` SHALL be encrypted at rest using `encrypt_value()` from `core/security.py`. The `legajo` field SHALL have a unique composite index with `tenant_id`.

#### Scenario: Create usuario with PII fields encrypts sensitive data

- **WHEN** a new Usuario is created with values for `dni`, `cuil`, and `cbu`
- **THEN** the database SHALL store these fields as encrypted ciphertext (base64 string) via `encrypt_value()`

#### Scenario: Usuario with duplicate legajo per tenant is rejected

- **WHEN** an INSERT or UPDATE attempts to set a `legajo` that already exists for the same `tenant_id`
- **THEN** the database SHALL raise a unique constraint violation

#### Scenario: Same legajo allowed across different tenants

- **WHEN** two usuarios in different tenants have the same `legajo` value
- **THEN** the database SHALL allow it (unique constraint is per tenant)

#### Scenario: PII fields are nullable on creation

- **WHEN** a Usuario is created without `dni`, `cuil`, `cbu`, `telefono`, `direccion`, `fecha_nacimiento`, or `legajo`
- **THEN** those fields SHALL be NULL in the database

### Requirement: Two-tier response schemas for usuario endpoints

The system SHALL provide two response schemas: `UsuarioResponse` (safe — excludes encrypted PII fields) and `UsuarioDetalleResponse` (includes decrypted PII fields). The list endpoint SHALL use `UsuarioResponse` only. The detail endpoint SHALL return `UsuarioDetalleResponse` with DNI, CUIL, and CBU decrypted only if the authenticated user has `usuarios:ver-pii` permission; otherwise, those fields SHALL be returned as None.

#### Scenario: List usuarios returns safe schema without PII

- **WHEN** an authenticated user with `usuarios:gestionar` sends a GET to `/api/admin/usuarios`
- **THEN** the response SHALL include `UsuarioResponse` items where `dni`, `cuil`, `cbu` are None (never returned)

#### Scenario: Detail usuario with ver-pii permission shows decrypted PII

- **WHEN** a user with both `usuarios:gestionar` and `usuarios:ver-pii` sends a GET to `/api/admin/usuarios/{id}`
- **THEN** the response SHALL include `UsuarioDetalleResponse` with decrypted `dni`, `cuil`, `cbu` (plaintext)

#### Scenario: Detail usuario without ver-pii permission shows PII as None

- **WHEN** a user with `usuarios:gestionar` but WITHOUT `usuarios:ver-pii` sends a GET to `/api/admin/usuarios/{id}`
- **THEN** the response SHALL include `UsuarioDetalleResponse` with `dni`, `cuil`, `cbu` as None

#### Scenario: Unauthenticated request to usuario endpoints returns 401

- **WHEN** a request without a valid JWT is sent to any `/api/admin/usuarios` endpoint
- **THEN** the system SHALL return `401 Unauthorized`

#### Scenario: Usuario update allows partial PII modification

- **WHEN** a PUT request to `/api/admin/usuarios/{id}` includes only `telefono` and `direccion`
- **THEN** only those fields SHALL be updated; other fields remain unchanged

#### Scenario: Usuario update encrypts modified PII fields

- **WHEN** a PUT request to `/api/admin/usuarios/{id}` includes a new `dni` value
- **THEN** the new value SHALL be encrypted via `encrypt_value()` before storage

### Requirement: Usuario list filtering and pagination

The system SHALL support filtering usuarios by `nombre`, `apellido`, `email`, `legajo`, and `is_active` query parameters. Results SHALL be paginated with `limit` (default 20, max 100) and `offset`. Filters SHALL be case-insensitive partial matches for text fields and exact matches for `is_active`.

#### Scenario: Filter usuarios by nombre partial match

- **WHEN** a GET request to `/api/admin/usuarios?nombre=Mar` includes a partial name
- **THEN** the response SHALL include usuarios whose `nombre` contains "Mar" (case-insensitive)

#### Scenario: Filter usuarios by legajo exact match

- **WHEN** a GET request to `/api/admin/usuarios?legajo=12345`
- **THEN** the response SHALL include the usuario with that exact legajo value

#### Scenario: Combined filters narrow results

- **WHEN** a GET request to `/api/admin/usuarios?is_active=true&apellido=Garcia`
- **THEN** the response SHALL include only active usuarios whose `apellido` contains "Garcia"

#### Scenario: Pagination limits usuario list response

- **WHEN** a GET request to `/api/admin/usuarios?limit=10&offset=20`
- **THEN** the response SHALL return at most 10 items starting from the 21st record, with `total` and `pages` metadata

### Requirement: Asignacion model CRUD

The system SHALL provide a full CRUD API for Asignacion under `/api/admin/asignaciones`. The Asignacion entity SHALL have fields: `id` (UUID PK), `tenant_id` (UUID FK), `usuario_id` (UUID FK to usuario, NOT NULL), `rol` (string, NOT NULL — maps to domain role names), `carrera_id` (UUID FK to carrera, nullable), `materia_id` (UUID FK to materia, nullable), `cohorte_id` (UUID FK to cohorte, nullable), `responsable_id` (UUID FK to usuario, nullable), `fecha_inicio` (date, NOT NULL), `fecha_fin` (date, nullable), `comisiones` (JSONB list of strings, default []), `is_active` (boolean, default True), standard timestamps and soft delete from BaseModelMixin.

#### Scenario: Create asignacion with valid data

- **WHEN** an authenticated user with `usuarios:asignar` sends a POST to `/api/admin/asignaciones` with valid `usuario_id`, `rol` (e.g. "PROFESOR"), `materia_id`, `fecha_inicio`, and `comisiones`
- **THEN** the system SHALL create the asignacion and return it with status `201`

#### Scenario: Create asignacion for nonexistent usuario returns 404

- **WHEN** a POST to `/api/admin/asignaciones` includes a `usuario_id` that does not exist
- **THEN** the system SHALL return `404 Not Found`

#### Scenario: Create asignacion with only usuario_id and rol (tenant-wide)

- **WHEN** a POST to `/api/admin/asignaciones` includes only `usuario_id` and `rol` (e.g. "ADMIN") with no academic context
- **THEN** the system SHALL create the asignacion with null `carrera_id`, `materia_id`, `cohorte_id`, and empty `comisiones`

#### Scenario: List asignaciones with pagination

- **WHEN** a GET request is sent to `/api/admin/asignaciones`
- **THEN** the system SHALL return all asignaciones for the current tenant (excluding soft-deleted), with pagination support

#### Scenario: Get asignacion by id

- **WHEN** a GET request is sent to `/api/admin/asignaciones/{id}` with a valid id
- **THEN** the system SHALL return the asignacion

#### Scenario: Update asignacion

- **WHEN** a PUT request is sent to `/api/admin/asignaciones/{id}` with valid fields (e.g., new `fecha_fin` or `comisiones`)
- **THEN** the system SHALL update the asignacion and return the updated record

#### Scenario: Soft delete asignacion

- **WHEN** a DELETE request is sent to `/api/admin/asignaciones/{id}`
- **THEN** the system SHALL soft-delete the asignacion and return `204`

### Requirement: Get user assignments

The system SHALL provide an endpoint `GET /api/admin/usuarios/{id}/asignaciones` that returns all active assignments for a specific user.

#### Scenario: Get assignments for a user

- **WHEN** a GET request is sent to `/api/admin/usuarios/{id}/asignaciones` with a valid usuario id
- **THEN** the system SHALL return all active (`is_active = True`, non-soft-deleted) asignaciones for that user

#### Scenario: Get assignments for nonexistent user returns 404

- **WHEN** a GET request is sent to `/api/admin/usuarios/{id}/asignaciones` with a non-existent usuario id
- **THEN** the system SHALL return `404 Not Found`

### Requirement: Permission guards for usuario and asignacion endpoints

All `/api/admin/usuarios` endpoints SHALL be guarded by `require_permission("usuarios:gestionar")`. All `/api/admin/asignaciones` endpoints SHALL be guarded by `require_permission("usuarios:asignar")`. The PII decryption in the detail endpoint SHALL additionally check `usuarios:ver-pii`.

#### Scenario: Usuario CRUD requires usuarios:gestionar

- **WHEN** a user WITHOUT `usuarios:gestionar` sends any request to `/api/admin/usuarios`
- **THEN** the system SHALL return `403 Forbidden`

#### Scenario: Asignacion CRUD requires usuarios:asignar

- **WHEN** a user WITHOUT `usuarios:asignar` sends any request to `/api/admin/asignaciones`
- **THEN** the system SHALL return `403 Forbidden`

### Requirement: Multi-tenant isolation for usuarios and asignaciones

Both entities SHALL be tenant-isolated. Users from tenant A SHALL NOT see usuarios or asignaciones from tenant B.

#### Scenario: Tenant isolation for usuario list

- **WHEN** a user from tenant A sends GET to `/api/admin/usuarios`
- **THEN** the response SHALL NOT include any usuarios from tenant B

#### Scenario: Tenant isolation for asignacion list

- **WHEN** a user from tenant A sends GET to `/api/admin/asignaciones`
- **THEN** the response SHALL NOT include any asignaciones from tenant B
