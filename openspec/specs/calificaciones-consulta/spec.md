# calificaciones-consulta Specification

## Purpose
TBD - created by archiving change c-10-calificaciones-y-umbral. Update Purpose after archive.
## Requirements
### Requirement: List calificaciones by materia and cohorte

The system SHALL expose `GET /api/v1/calificaciones?materia_id=&cohorte_id=` that returns paginated calificaciones filtered by materia and cohorte, scoped to the current tenant.

#### Scenario: List calificaciones with filters

- **WHEN** a user requests calificaciones with valid `materia_id` and `cohorte_id`
- **THEN** the system SHALL return a paginated list of matching calificaciones for the current tenant

#### Scenario: List returns empty for no matches

- **WHEN** a user requests calificaciones for a materia/cohorte with no records
- **THEN** the system SHALL return an empty list

#### Scenario: List is tenant-scoped

- **WHEN** tenant A lists calificaciones
- **THEN** calificaciones belonging to tenant B SHALL NOT appear in the response

