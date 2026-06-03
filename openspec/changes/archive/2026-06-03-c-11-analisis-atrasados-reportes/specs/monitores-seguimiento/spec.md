## ADDED Requirements

### Requirement: Provide monitor for tutor/profesor scope
The system SHALL provide a monitor view for `TUTOR` and `PROFESOR` restricted to alumnos under their active assignments, with filters for alumno, email, comisión, regional, actividad and minimum completion threshold.

#### Scenario: Tutor/profesor sees only assigned students
- **WHEN** a tutor/profesor queries monitor data
- **THEN** the response SHALL include only alumnos within that actor's active assignment scope

#### Scenario: Tutor/profesor filters are applied
- **WHEN** tutor/profesor sends monitor filters (alumno/email/comisión/regional/actividad/min completion)
- **THEN** the response SHALL apply all provided filters conjunctively

### Requirement: Provide monitor for coordinacion/admin scope with date range
The system SHALL provide a monitor view for `COORDINADOR` and `ADMIN` over tenant-wide data, supporting all tutor/profesor filters plus required date-range filtering.

#### Scenario: Coordinacion/admin can filter by date range
- **WHEN** a coordinacion/admin user queries monitor with `from_date` and `to_date`
- **THEN** the system SHALL return only rows within the requested range

#### Scenario: Invalid date range is rejected
- **WHEN** `from_date` is later than `to_date`
- **THEN** the system SHALL return `400 Bad Request`

### Requirement: Paginate monitor results
The system SHALL paginate monitor results and return deterministic ordering for repeated requests with the same filter set.

#### Scenario: Monitor returns paginated response
- **WHEN** monitor query matches more rows than page size
- **THEN** the system SHALL return current page data plus pagination metadata

#### Scenario: Repeated query order is stable
- **WHEN** the same monitor query is executed multiple times without underlying data changes
- **THEN** rows SHALL appear in the same order across responses
