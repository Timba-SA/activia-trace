## ADDED Requirements

### Requirement: Compute alumnos atrasados by materia/cohorte
The system SHALL compute alumnos atrasados for a selected `materia_id` and `cohorte_id`, where an alumno is considered atrasado when at least one required actividad is missing OR has calificacion below the configured umbral for that materia.

#### Scenario: Atrasado by missing activity
- **WHEN** an alumno has at least one required actividad without calificacion registrada
- **THEN** the alumno SHALL be included in the atrasados result

#### Scenario: Atrasado by calificacion below umbral
- **WHEN** an alumno has calificacion registrada but at least one actividad is below `umbral_pct`
- **THEN** the alumno SHALL be included in the atrasados result

#### Scenario: Not atrasado when all activities approved
- **WHEN** an alumno has all required actividades with calificacion meeting approval criteria
- **THEN** the alumno SHALL NOT be included in the atrasados result

### Requirement: Build ranking of approved activities
The system SHALL provide a ranking ordered by descending count of actividades aprobadas per alumno, including only alumnos with at least one actividad aprobada.

#### Scenario: Ranking excludes zero-approved students
- **WHEN** an alumno has zero actividades aprobadas
- **THEN** the alumno SHALL be excluded from ranking output

#### Scenario: Ranking order is descending
- **WHEN** multiple alumnos have different counts of actividades aprobadas
- **THEN** the result SHALL be sorted from highest to lowest approved count

### Requirement: Provide quick report by materia
The system SHALL provide a quick report for the selected materia/cohorte including totals and percentages for: alumnos evaluados, alumnos atrasados, alumnos sin atrasos, and actividades pendientes de corrección detectadas.

#### Scenario: Report returns aggregate metrics
- **WHEN** report endpoint is queried for a materia/cohorte with data
- **THEN** the response SHALL include aggregate totals and percentages for the required metrics

#### Scenario: Report handles no-data state
- **WHEN** report endpoint is queried for a materia/cohorte without calificaciones
- **THEN** the response SHALL return zero-valued metrics and a non-error empty state

### Requirement: Provide grouped final grades
The system SHALL return final grouped grades per alumno for selected activity groups, using the configured aggregation rule for this change and exposing both group values and overall final value.

#### Scenario: Final grade grouped by selected activities
- **WHEN** user requests grouped final grades with valid activity groups
- **THEN** the system SHALL calculate and return one grouped value per group and one overall final value per alumno

#### Scenario: Missing group data is explicit
- **WHEN** an alumno has no data for one selected group
- **THEN** the response SHALL include explicit null/empty value for that group without failing the full result

### Requirement: Guard all analysis endpoints with atrasados:ver
All `/api/analisis/*` endpoints SHALL require `require_permission("atrasados:ver")` and SHALL derive actor identity and tenant scope exclusively from the authenticated session.

#### Scenario: Unauthorized request is rejected
- **WHEN** a user without `atrasados:ver` calls an analysis endpoint
- **THEN** the system SHALL return `403 Forbidden`

#### Scenario: Session identity overrides request hints
- **WHEN** a request includes optional scope hints (e.g., user/materia identifiers) outside the actor's allowed scope
- **THEN** the system SHALL ignore external identity hints and enforce session-derived scope
