### Requirement: COORDINADOR/PROFESOR/ADMIN can create tareas

The system SHALL allow users with the `tareas:gestionar` permission to create Tarea records with the following fields: asignado_a (UUID FK Usuario, NOT NULL), asignado_por (UUID FK Usuario, NOT NULL), materia_id (UUID FK Materia, nullable), contexto_id (UUID, nullable), descripcion (string, NOT NULL). The initial estado SHALL be "Pendiente".

#### Scenario: Create tarea with valid data

- **WHEN** a user with `tareas:gestionar` sends a POST request with valid tarea data (asignado_a, descripcion)
- **THEN** the system SHALL return `201 Created` with the created tarea data including id and estado = "Pendiente"

#### Scenario: Create tarea without materia_id

- **WHEN** a user with `tareas:gestionar` sends a POST request without materia_id
- **THEN** the system SHALL return `201 Created` with materia_id = null

#### Scenario: Create tarea without permission returns 403

- **WHEN** a user without `tareas:gestionar` sends a POST request to create a tarea
- **THEN** the system SHALL return `403 Forbidden`

### Requirement: Users can list their assigned tareas

The system SHALL allow any authenticated user with `tareas:gestionar` to GET /api/tareas and receive only tareas where asignado_a equals the authenticated user's id. Results SHALL be ordered by created_at DESC.

#### Scenario: List mis tareas returns only assigned tasks

- **WHEN** a user with `tareas:gestionar` sends GET /api/tareas
- **THEN** the response SHALL include only tareas where asignado_a = current user id

#### Scenario: Mis tareas is empty when no assignments

- **WHEN** a user has no tareas assigned
- **THEN** the response SHALL return an empty list

### Requirement: COORDINADOR/ADMIN can view all tareas with filters

The system SHALL allow COORDINADOR and ADMIN users to GET /api/tareas/admin with optional query filters: asignado_a (UUID), asignado_por (UUID), materia_id (UUID), estado (enum), q (string — search in descripcion). Results SHALL be scoped to the current tenant.

#### Scenario: Admin list returns all tenant tareas

- **WHEN** a COORDINADOR or ADMIN sends GET /api/tareas/admin without filters
- **THEN** the response SHALL include all non-soft-deleted tareas for the tenant

#### Scenario: Admin list filtered by estado

- **WHEN** a COORDINADOR sends GET /api/tareas/admin?estado=Pendiente
- **THEN** the response SHALL include only tareas with estado = "Pendiente"

#### Scenario: Admin list filtered by asignado_a

- **WHEN** a COORDINADOR sends GET /api/tareas/admin?asignado_a=<usuario_id>
- **THEN** the response SHALL include only tareas assigned to that usuario

#### Scenario: Admin list filtered by search in descripcion

- **WHEN** a COORDINADOR sends GET /api/tareas/admin?q=corrección
- **THEN** the response SHALL include only tareas whose descripcion contains "corrección" (case-insensitive)

### Requirement: Users can get tarea detail

The system SHALL allow any user with `tareas:gestionar` to GET /api/tareas/{id} and receive the full tarea data, including asignado_a and asignado_por user info. The tarea MUST belong to the same tenant.

#### Scenario: Get tarea by id returns full detail

- **WHEN** a user with `tareas:gestionar` sends GET /api/tareas/{id} with a valid tarea id
- **THEN** the system SHALL return `200 OK` with the tarea detail

#### Scenario: Get tarea from different tenant returns 404

- **WHEN** a user requests a tarea from a different tenant
- **THEN** the system SHALL return `404 Not Found`

### Requirement: Users can update tarea estado and reasignar

The system SHALL allow users with `tareas:gestionar` to PATCH /api/tareas/{id} to change estado or reasignar (cambiar asignado_a). Estado transitions SHALL follow FL-05 rules: Pendiente→En progreso, Pendiente→Cancelada (COORDINADOR/ADMIN), En progreso→Resuelta, En progreso→Cancelada (COORDINADOR/ADMIN), Resuelta→Pendiente (solo COORDINADOR/ADMIN — devolución). COORDINADOR/ADMIN can Cancelar from any estado.

#### Scenario: Asignado changes estado from Pendiente to En progreso

- **WHEN** the asignado user PATCHes estado to "En progreso"
- **THEN** the system SHALL update estado and return `200 OK`

#### Scenario: Asignado changes estado from En progreso to Resuelta

- **WHEN** the asignado user PATCHes estado to "Resuelta"
- **THEN** the system SHALL update estado and return `200 OK`

#### Scenario: Invalid transition Resuelta to Pendiente by asignado returns 409

- **WHEN** the asignado user PATCHes estado from "Resuelta" to "Pendiente"
- **THEN** the system SHALL return `409 Conflict`

#### Scenario: COORDINADOR can Cancel tarea from any estado

- **WHEN** a COORDINADOR PATCHes estado to "Cancelada" on a tarea in any estado
- **THEN** the system SHALL return `200 OK`

#### Scenario: COORDINADOR can devolver tarea (Resuelta to Pendiente)

- **WHEN** a COORDINADOR PATCHes estado from "Resuelta" to "Pendiente"
- **THEN** the system SHALL return `200 OK`

#### Scenario: Reasignar tarea to another docente

- **WHEN** a user with `tareas:gestionar` PATCHes asignado_a to a new usuario_id
- **THEN** the system SHALL update asignado_a and return the updated tarea

### Requirement: Users can add comments to tareas

The system SHALL allow any user with `tareas:gestionar` to POST /api/tareas/{id}/comentarios with a texto field. The system SHALL create a ComentarioTarea record with the current user as autor_id and the current timestamp.

#### Scenario: Add comment to tarea

- **WHEN** a user with `tareas:gestionar` sends POST /api/tareas/{id}/comentarios with valid texto
- **THEN** the system SHALL create a ComentarioTarea record and return `201 Created`

#### Scenario: Add comment to nonexistent tarea returns 404

- **WHEN** a user sends POST /api/tareas/{id}/comentarios with a non-existent tarea id
- **THEN** the system SHALL return `404 Not Found`

#### Scenario: List comments for tarea

- **WHEN** a user with `tareas:gestionar` sends GET /api/tareas/{id}/comentarios
- **THEN** the system SHALL return all ComentarioTarea records for that tarea, ordered by creado_at ASC

#### Scenario: List comments for nonexistent tarea returns empty list

- **WHEN** a user sends GET /api/tareas/{id}/comentarios with a non-existent tarea id
- **THEN** the system SHALL return an empty list

### Requirement: Tareas and ComentarioTarea have soft delete

Both Tarea and ComentarioTarea SHALL support soft delete via a `deleted_at` column.

#### Scenario: Soft-deleted tarea excluded from lists

- **WHEN** a tarea has `deleted_at` set
- **THEN** it SHALL NOT appear in mis-tareas or admin list responses

#### Scenario: Soft-deleted tarea detail returns 404

- **WHEN** a user requests GET /api/tareas/{id} for a soft-deleted tarea
- **THEN** the system SHALL return `404 Not Found`
