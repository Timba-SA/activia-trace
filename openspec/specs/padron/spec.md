## ADDED Requirements

### Requirement: VersionPadron model

The system SHALL provide a `VersionPadron` entity with fields: `id` (UUID PK), `tenant_id` (UUID FK), `materia_id` (UUID FK to Materia), `cohorte_id` (UUID FK to Cohorte), `activa` (boolean), `creada_por` (UUID FK to Usuario), standard timestamps and soft delete from BaseModelMixin.

#### Scenario: Only one active version per materia+cohorte

- **WHEN** a new version is activated for `(materia_id, cohorte_id)` that already has an active version
- **THEN** the previous active version SHALL be deactivated (activa = false) and the new version SHALL become the active one

#### Scenario: Version isolation by tenant

- **WHEN** querying versions for tenant A
- **THEN** versions from tenant B SHALL NOT be visible

#### Scenario: Get active version

- **WHEN** querying the active version for a `(materia_id, cohorte_id)` that has one
- **THEN** the system SHALL return the active version

#### Scenario: No active version returns None

- **WHEN** querying the active version for a `(materia_id, cohorte_id)` with no versions
- **THEN** the system SHALL return null/None

### Requirement: EntradaPadron model

The system SHALL provide an `EntradaPadron` entity with fields: `id` (UUID PK), `tenant_id` (UUID FK), `version_padron_id` (UUID FK), `usuario_id` (UUID FK to Usuario, nullable), `legajo` (string), `nombre_completo` (string), `email` (string), `estado` (string, e.g. "activo"), `datos_extra` (JSONB nullable), standard timestamps.

#### Scenario: Entrada without usuario_id

- **WHEN** an entrada is created with `usuario_id = null`
- **THEN** the system SHALL accept it (student without account is valid per KB E6)

#### Scenario: Entrada list by version

- **WHEN** querying entradas by `version_padron_id`
- **THEN** the system SHALL return all entradas belonging to that version for the current tenant

### Requirement: Upload flow — file to preview

The system SHALL accept xlsx/csv file upload for a given `(materia_id, cohorte_id)`, parse the file, and return a preview with the parsed rows ready for confirmation.

#### Scenario: Preview uploaded file

- **WHEN** a user with `padron:cargar` uploads an xlsx/csv file with valid columns (legajo, nombre_completo, email)
- **THEN** the system SHALL return a preview with the parsed rows and a preview hash

#### Scenario: Preview requires padron:cargar

- **WHEN** a user without `padron:cargar` tries to upload
- **THEN** the system SHALL return `403 Forbidden`

### Requirement: Confirm upload — create version + entradas

The system SHALL accept a confirmation request that creates a new VersionPadron (deactivating the previous active one) and all EntradaPadron rows.

#### Scenario: Confirm creates version and entradas

- **WHEN** a user confirms a preview
- **THEN** the system SHALL create a new VersionPadron with `activa = true`, deactivate any previous active version for the same (materia, cohorte), and create all EntradaPadron rows

### Requirement: Permission guard

All padron endpoints SHALL be guarded by `require_permission("padron:cargar")`.

#### Scenario: Authorized user can access endpoint

- **WHEN** a user with `padron:cargar` permission sends any request to padron endpoints
- **THEN** the request SHALL proceed to the endpoint handler

#### Scenario: Unauthorized user receives 403

- **WHEN** a user without `padron:cargar` permission sends any request to padron endpoints
- **THEN** the system SHALL return `403 Forbidden`

### Requirement: Moodle WS client stub

The system SHALL include a module `integrations/moodle_ws.py` with an async client class for Moodle Web Services.

#### Scenario: MoodleWSClient can be instantiated

- **WHEN** MoodleWSClient is instantiated with valid base_url and token
- **THEN** it SHALL have the correct base_url configured
