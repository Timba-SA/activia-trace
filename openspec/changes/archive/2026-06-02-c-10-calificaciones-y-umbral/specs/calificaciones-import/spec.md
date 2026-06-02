## ADDED Requirements

### Requirement: Calificacion model

The system SHALL provide a `Calificacion` entity with fields: `id` (UUID PK), `tenant_id` (UUID FK), `entrada_padron_id` (UUID FK to EntradaPadron), `materia_id` (UUID FK to Materia), `cohorte_id` (UUID FK to Cohorte), `usuario_id` (UUID FK to Usuario, nullable), `actividad_nombre` (string), `calificacion` (string), `es_numerica` (bool), `aprobado` (bool, denormalized), `origen` (enum string: "Importado" | "Manual"), `metadata_json` (JSONB nullable), standard timestamps and soft delete from BaseModelMixin.

#### Scenario: Calificacion creation with numeric grade

- **WHEN** a `Calificacion` is created with `calificacion = "8.5"`, `es_numerica = True`, `origen = "Importado"`
- **THEN** the system SHALL store the record and compute `aprobado` based on the materia's umbral

#### Scenario: Calificacion creation with textual grade

- **WHEN** a `Calificacion` is created with `calificacion = "Aprobado"`, `es_numerica = False`, `origen = "Importado"`
- **THEN** the system SHALL store the record and compute `aprobado` by checking against `valores_aprobados`

#### Scenario: Calificacion belongs to tenant

- **WHEN** querying calificaciones for tenant A
- **THEN** calificaciones from tenant B SHALL NOT be visible

### Requirement: Import preview — file to column detection

The system SHALL accept a file upload (CSV) for a given `(materia_id, cohorte_id)`, parse columns, detect numeric vs textual activity columns, and return a preview with per-student values and a preview hash.

#### Scenario: Preview detects numeric columns

- **WHEN** a user uploads a CSV file where all values in a column parse as float
- **THEN** the system SHALL mark that column as `es_numerica = True`

#### Scenario: Preview detects textual columns

- **WHEN** a user uploads a CSV file where at least one value in a column fails `float()` conversion
- **THEN** the system SHALL mark that column as `es_numerica = False`

#### Scenario: Preview returns rows with student data

- **WHEN** a user uploads a valid CSV with columns [legajo, nombre_completo, email, Actividad1, Actividad2]
- **THEN** the system SHALL return parsed rows with student identification and activity values

#### Scenario: Preview requires calificaciones:importar

- **WHEN** a user without `calificaciones:importar` permission tries to upload
- **THEN** the system SHALL return `403 Forbidden`

#### Scenario: Preview returns preview_hash

- **WHEN** a preview is generated
- **THEN** the response SHALL include a `preview_hash` computed from the parsed data

### Requirement: Import confirm — bulk create calificaciones

The system SHALL accept a confirmation request with selected activities and preview hash, verify the hash, and bulk create Calificacion records with derived `aprobado`.

#### Scenario: Confirm creates calificaciones

- **WHEN** a user confirms with valid preview_hash and selected activities
- **THEN** the system SHALL create Calificacion records for each student x activity combination with derived `aprobado`

#### Scenario: Confirm rejects changed data

- **WHEN** a user confirms with a preview_hash that doesn't match the data
- **THEN** the system SHALL return `400 Bad Request` with an error message

#### Scenario: Aprobado derivation for numeric

- **WHEN** a numeric grade `calificacion >= umbral_pct * 0.01 * max_nota`
- **THEN** `aprobado` SHALL be `True`

#### Scenario: Aprobado derivation for textual

- **WHEN** a textual grade is in the materia's `valores_aprobados` list
- **THEN** `aprobado` SHALL be `True`

#### Scenario: Aprobado derivation for non-approved textual

- **WHEN** a textual grade is NOT in the materia's `valores_aprobados` list
- **THEN** `aprobado` SHALL be `False`

### Requirement: Permission guard

All calificaciones import endpoints SHALL be guarded by `require_permission("calificaciones:importar")`.

#### Scenario: Authorized user can access import endpoints

- **WHEN** a user with `calificaciones:importar` permission sends requests to import endpoints
- **THEN** the request SHALL proceed to the endpoint handler

#### Scenario: Unauthorized user receives 403 on import endpoints

- **WHEN** a user without `calificaciones:importar` sends requests to import endpoints
- **THEN** the system SHALL return `403 Forbidden`
