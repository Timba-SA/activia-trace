## ADDED Requirements

### Requirement: Carrera model

The system SHALL provide a `Carrera` entity with fields: `id` (UUID PK), `tenant_id` (UUID FK), `codigo` (string, unique per tenant), `nombre` (string), `descripcion` (string, nullable), `duracion_anios` (int, nullable), `is_active` (boolean, default True), standard timestamps and soft delete from BaseModelMixin.

#### Scenario: Create carrera

- **WHEN** an authenticated user with `estructura:gestionar` permission sends a POST request to `/api/admin/carreras` with valid `codigo`, `nombre`, and optional `descripcion` and `duracion_anios`
- **THEN** the system SHALL create a new carrera and return it with status `201`

#### Scenario: Create carrera with duplicate codigo per tenant

- **WHEN** a POST request to `/api/admin/carreras` includes a `codigo` that already exists for the current tenant
- **THEN** the system SHALL return `409 Conflict`

#### Scenario: Create carrera with same codigo in different tenant

- **WHEN** a POST request to `/api/admin/carreras` from tenant A includes a `codigo` that already exists for tenant B but NOT for tenant A
- **THEN** the system SHALL create the carrera successfully with status `201`

#### Scenario: List carreras

- **WHEN** a GET request is sent to `/api/admin/carreras`
- **THEN** the system SHALL return all carreras for the current tenant (excluding soft-deleted), with pagination support

#### Scenario: Get carrera by id

- **WHEN** a GET request is sent to `/api/admin/carreras/{id}` with a valid carrera id
- **THEN** the system SHALL return the carrera

#### Scenario: Get carrera by id not found

- **WHEN** a GET request is sent to `/api/admin/carreras/{id}` with a non-existent id
- **THEN** the system SHALL return `404 Not Found`

#### Scenario: Update carrera

- **WHEN** a PUT request is sent to `/api/admin/carreras/{id}` with valid fields
- **THEN** the system SHALL update the carrera and return the updated record

#### Scenario: Soft delete carrera

- **WHEN** a DELETE request is sent to `/api/admin/carreras/{id}` for a carrera with no non-deleted cohorts
- **THEN** the system SHALL soft-delete the carrera and return `204`

#### Scenario: Delete carrera with existing cohorts is rejected

- **WHEN** a DELETE request is sent to `/api/admin/carreras/{id}` for a carrera that has at least one non-deleted cohort
- **THEN** the system SHALL return `409 Conflict` with a message indicating cohorts exist

### Requirement: Cohorte model

The system SHALL provide a `Cohorte` entity with fields: `id` (UUID PK), `tenant_id` (UUID FK), `carrera_id` (UUID FK to Carrera, not nullable), `nombre` (string, unique per tenant + carrera), `anio` (int), `is_active` (boolean, default True), standard timestamps and soft delete from BaseModelMixin.

#### Scenario: Create cohorte

- **WHEN** an authenticated user with `estructura:gestionar` permission sends a POST request to `/api/admin/cohortes` with valid `carrera_id`, `nombre`, and `anio` for an active carrera
- **THEN** the system SHALL create a new cohorte and return it with status `201`

#### Scenario: Create cohorte with duplicate nombre per carrera

- **WHEN** a POST request to `/api/admin/cohortes` includes a `nombre` that already exists for the same `(tenant_id, carrera_id)` combination
- **THEN** the system SHALL return `409 Conflict`

#### Scenario: Create cohorte for inactive carrera is rejected

- **WHEN** a POST request to `/api/admin/cohortes` references a `carrera_id` whose `is_active` is `False`
- **THEN** the system SHALL return `400 Bad Request` indicating the carrera is inactive

#### Scenario: List cohortes

- **WHEN** a GET request is sent to `/api/admin/cohortes`
- **THEN** the system SHALL return all cohortes for the current tenant (excluding soft-deleted), with optional filter by `carrera_id` and pagination support

#### Scenario: Get cohorte by id

- **WHEN** a GET request is sent to `/api/admin/cohortes/{id}` with a valid cohorte id
- **THEN** the system SHALL return the cohorte

#### Scenario: Update cohorte

- **WHEN** a PUT request is sent to `/api/admin/cohortes/{id}` with valid fields
- **THEN** the system SHALL update the cohorte and return the updated record

#### Scenario: Soft delete cohorte

- **WHEN** a DELETE request is sent to `/api/admin/cohortes/{id}`
- **THEN** the system SHALL soft-delete the cohorte and return `204`

### Requirement: Materia model

The system SHALL provide a `Materia` entity with fields: `id` (UUID PK), `tenant_id` (UUID FK), `carrera_id` (UUID FK to Carrera, nullable), `codigo` (string, unique per tenant), `nombre` (string), `descripcion` (string, nullable), `carga_horaria` (int, nullable), `is_active` (boolean, default True), standard timestamps and soft delete from BaseModelMixin.

#### Scenario: Create materia

- **WHEN** an authenticated user with `estructura:gestionar` permission sends a POST request to `/api/admin/materias` with valid `codigo` and `nombre`, and optional `carrera_id`, `descripcion`, `carga_horaria`
- **THEN** the system SHALL create a new materia and return it with status `201`

#### Scenario: Create materia without carrera

- **WHEN** a POST request to `/api/admin/materias` omits `carrera_id`
- **THEN** the system SHALL create the materia successfully with `carrera_id = null` (catalog-level materia)

#### Scenario: Create materia with duplicate codigo per tenant

- **WHEN** a POST request to `/api/admin/materias` includes a `codigo` that already exists for the current tenant
- **THEN** the system SHALL return `409 Conflict`

#### Scenario: Create materia with same codigo in different tenant

- **WHEN** a POST request to `/api/admin/materias` from tenant A includes a `codigo` that already exists for tenant B but NOT for tenant A
- **THEN** the system SHALL create the materia successfully with status `201`

#### Scenario: List materias

- **WHEN** a GET request is sent to `/api/admin/materias`
- **THEN** the system SHALL return all materias for the current tenant (excluding soft-deleted), with optional filter by `carrera_id` and pagination support

#### Scenario: Get materia by id

- **WHEN** a GET request is sent to `/api/admin/materias/{id}` with a valid materia id
- **THEN** the system SHALL return the materia

#### Scenario: Update materia

- **WHEN** a PUT request is sent to `/api/admin/materias/{id}` with valid fields
- **THEN** the system SHALL update the materia and return the updated record

#### Scenario: Soft delete materia

- **WHEN** a DELETE request is sent to `/api/admin/materias/{id}`
- **THEN** the system SHALL soft-delete the materia and return `204`

### Requirement: Multi-tenant isolation

All three entities MUST be tenant-isolated. Users from tenant A MUST NOT see, create, update, or delete records belonging to tenant B. Repository-layer tenant scoping (via `BaseRepository._apply_tenant_scope`) provides this automatically.

#### Scenario: Tenant A cannot see tenant B's carreras

- **WHEN** user from tenant A sends a GET request to `/api/admin/carreras`
- **THEN** the response SHALL NOT include any carreras from tenant B

#### Scenario: Tenant A cannot see tenant B's cohortes

- **WHEN** user from tenant A sends a GET request to `/api/admin/cohortes`
- **THEN** the response SHALL NOT include any cohortes from tenant B

#### Scenario: Tenant A cannot see tenant B's materias

- **WHEN** user from tenant A sends a GET request to `/api/admin/materias`
- **THEN** the response SHALL NOT include any materias from tenant B

### Requirement: Permission guard

All admin endpoints SHALL be guarded by `require_permission("estructura:gestionar")`. Only users with the `estructura:gestionar` permission in their resolved permission set SHALL access these endpoints.

#### Scenario: Authorized user can access

- **WHEN** a user with `estructura:gestionar` permission sends any request to `/api/admin/carreras`, `/api/admin/cohortes`, or `/api/admin/materias`
- **THEN** the request SHALL proceed to the endpoint handler

#### Scenario: Unauthorized user receives 403

- **WHEN** a user without `estructura:gestionar` permission sends any request to `/api/admin/carreras`, `/api/admin/cohortes`, or `/api/admin/materias`
- **THEN** the system SHALL return `403 Forbidden`
