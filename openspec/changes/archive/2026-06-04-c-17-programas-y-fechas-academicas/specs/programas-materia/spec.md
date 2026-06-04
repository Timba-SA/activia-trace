## ADDED Requirements

### Requirement: COORDINADOR and ADMIN can manage program documents

The system SHALL allow users with the `programas:gestionar` permission (COORDINADOR, ADMIN) to create, read, update, and deactivate program documents for a subject (materia), career (carrera), and optionally cohort (cohorte).

- Each programa SHALL have a unique ID, tenant_id, materia_id, carrera_id, optional cohorte_id, titulo, referencia_archivo, optional contenido_html, version (integer), activo (boolean), and optional aprobado_en (date).
- Creating a new program for the same materia + carrera + cohorte SHALL automatically increment the version and deactivate the previous active version.

#### Scenario: Create a new program document

- **WHEN** a COORDINADOR sends a POST to `/api/programas` with `materia_id`, `carrera_id`, `cohorte_id`, `titulo`, `referencia_archivo`
- **THEN** the system SHALL return 201 with the created program data, version = 1, activo = true

#### Scenario: Create a new version of an existing program

- **WHEN** a COORDINADOR sends a POST to `/api/programas` for the same materia_id + carrera_id + cohorte combination that already has an active program
- **THEN** the system SHALL create a new program with version = previous_version + 1, activo = true, and SHALL set the previous active program's activo to false

#### Scenario: List programs with filters

- **WHEN** a COORDINADOR sends a GET to `/api/programas?materia_id=UUID&carrera_id=UUID`
- **THEN** the system SHALL return 200 with a paginated list of programs matching the filters, excluding inactive programs by default

#### Scenario: Get program detail

- **WHEN** any user with `programas:ver` or `programas:gestionar` sends a GET to `/api/programas/{id}`
- **THEN** the system SHALL return 200 with full program details including materia and carrera names

#### Scenario: Update a program

- **WHEN** a COORDINADOR sends a PATCH to `/api/programas/{id}` with fields to update
- **THEN** the system SHALL return 200 with the updated program data, keeping version unchanged

#### Scenario: Deactivate a program (soft delete)

- **WHEN** a COORDINADOR sends a DELETE to `/api/programas/{id}`
- **THEN** the system SHALL set `activo = false` and return 204, keeping the record for historical reference

#### Scenario: 403 without programas:gestionar permission on write operations

- **WHEN** a user without `programas:gestionar` sends POST, PATCH, or DELETE to `/api/programas`
- **THEN** the system SHALL return 403 Forbidden

### Requirement: System can generate HTML content from a program

The system SHALL generate an HTML fragment ready for LMS publication from an active program document.

#### Scenario: Generate content from active program

- **WHEN** a COORDINADOR sends a POST to `/api/programas/{id}/generar-contenido` and the program exists and is active
- **THEN** the system SHALL return 200 with a `contenido_html` string containing formatted HTML with program title, materia name, carrera name, and reference file link

#### Scenario: Generate content from inactive program returns 404

- **WHEN** a COORDINADOR sends a POST to `/api/programas/{id}/generar-contenido` and the program exists but `activo = false`
- **THEN** the system SHALL return 404 Not Found
