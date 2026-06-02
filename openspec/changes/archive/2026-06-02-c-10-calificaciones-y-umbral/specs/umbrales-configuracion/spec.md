## ADDED Requirements

### Requirement: UmbralMateria model

The system SHALL provide an `UmbralMateria` entity with fields: `id` (UUID PK), `tenant_id` (UUID FK), `materia_id` (UUID FK to Materia), `cohorte_id` (UUID FK to Cohorte, nullable), `umbral_pct` (float, default 60.0), `valores_aprobados` (JSONB list of strings), standard timestamps and soft delete.

#### Scenario: Default umbral is 60%

- **WHEN** an `UmbralMateria` is created without specifying `umbral_pct`
- **THEN** the system SHALL set `umbral_pct = 60.0`

#### Scenario: Umbral is tenant-scoped

- **WHEN** querying umbrales for tenant A
- **THEN** umbrales from tenant B SHALL NOT be visible

### Requirement: Get umbral by materia

The system SHALL expose `GET /api/v1/umbrales?materia_id=` that returns the umbral configuration for a materia, or a default object if none exists.

#### Scenario: Get existing umbral

- **WHEN** querying umbrales for a materia that has one configured
- **THEN** the system SHALL return the umbral configuration

#### Scenario: Get default umbral when none exists

- **WHEN** querying umbrales for a materia without explicit configuration
- **THEN** the system SHALL return a default umbral object with `umbral_pct = 60.0`, `valores_aprobados = ["Aprobado", "Promocionado"]`

### Requirement: Update umbral

The system SHALL expose `PUT /api/v1/umbrales/{id}` that updates `umbral_pct` and/or `valores_aprobados`.

#### Scenario: Update umbral_pct

- **WHEN** a user with `calificaciones:configurar-umbral` updates `umbral_pct` to 75.0
- **THEN** the system SHALL update the umbral and return the new configuration

#### Scenario: Update valores_aprobados

- **WHEN** a user updates `valores_aprobados` to ["Aprobado", "Muy bueno", "Excelente"]
- **THEN** the system SHALL update the list and return the new configuration

#### Scenario: Update requires permission

- **WHEN** a user without `calificaciones:configurar-umbral` tries to update
- **THEN** the system SHALL return `403 Forbidden`

#### Scenario: Umbral update does not affect other materias

- **WHEN** updating umbral for materia A
- **THEN** the umbral for materia B SHALL remain unchanged
