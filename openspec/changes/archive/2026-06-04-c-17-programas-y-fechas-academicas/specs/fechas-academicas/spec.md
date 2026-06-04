## ADDED Requirements

### Requirement: COORDINADOR and ADMIN can manage academic dates

The system SHALL allow users with the `programas:gestionar` permission (COORDINADOR, ADMIN) to create, read, update, and delete academic dates (exam instances) for a subject (materia) and cohort (cohorte).

- Each fecha academica SHALL have a unique ID, tenant_id, materia_id, cohorte_id, tipo (Parcial | TP | Coloquio | Recuperatorio), optional numero, fecha, optional hora, optional aula, and optional observaciones.
- Dates SHALL be soft-deleted (deleted_at timestamp).

#### Scenario: Create a new academic date

- **WHEN** a COORDINADOR sends a POST to `/api/fechas-academicas` with `materia_id`, `cohorte_id`, `tipo`, `fecha`, and optional fields
- **THEN** the system SHALL return 201 with the created date data

#### Scenario: List academic dates with filters

- **WHEN** a COORDINADOR sends a GET to `/api/fechas-academicas?materia_id=UUID&cohorte_id=UUID&tipo=Parcial`
- **THEN** the system SHALL return 200 with a paginated list of dates matching the filters, excluding soft-deleted records

#### Scenario: Get academic date detail

- **WHEN** any user with `programas:ver` or `programas:gestionar` sends a GET to `/api/fechas-academicas/{id}`
- **THEN** the system SHALL return 200 with full date details including materia and cohorte names

#### Scenario: Update an academic date

- **WHEN** a COORDINADOR sends a PATCH to `/api/fechas-academicas/{id}` with fields to update
- **THEN** the system SHALL return 200 with the updated date data

#### Scenario: Delete an academic date (soft delete)

- **WHEN** a COORDINADOR sends a DELETE to `/api/fechas-academicas/{id}`
- **THEN** the system SHALL soft delete the record and return 204

#### Scenario: 403 without programas:gestionar permission on write operations

- **WHEN** a user without `programas:gestionar` sends POST, PATCH, or DELETE to `/api/fechas-academicas`
- **THEN** the system SHALL return 403 Forbidden
