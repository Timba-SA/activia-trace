## MODIFIED Requirements

### Requirement: List calificaciones by materia and cohorte

The system SHALL expose `GET /api/v1/calificaciones?materia_id=&cohorte_id=` that returns paginated calificaciones filtered by materia and cohorte, scoped to the current tenant, and SHALL support optional aggregate fields required by analysis/reporting (`aprobadas_count`, `desaprobadas_count`, `faltantes_count` by alumno).

#### Scenario: List calificaciones with filters

- **WHEN** a user requests calificaciones with valid `materia_id` and `cohorte_id`
- **THEN** the system SHALL return a paginated list of matching calificaciones for the current tenant

#### Scenario: List returns empty for no matches

- **WHEN** a user requests calificaciones for a materia/cohorte with no records
- **THEN** the system SHALL return an empty list

#### Scenario: List is tenant-scoped

- **WHEN** tenant A lists calificaciones
- **THEN** calificaciones belonging to tenant B SHALL NOT appear in the response

#### Scenario: Optional analysis aggregates are returned when requested

- **WHEN** a client requests calificaciones with analysis aggregate mode enabled
- **THEN** the response SHALL include per-alumno aggregate counters (`aprobadas_count`, `desaprobadas_count`, `faltantes_count`) computed from the same tenant-scoped dataset
