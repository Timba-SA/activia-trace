## ADDED Requirements

### Requirement: Detect potential entregas sin corregir
The system SHALL detect potential entregas sin corregir by correlating activity finalization input with existing calificaciones and marking entries where finalization exists but no calificacion was registered for the same alumno-actividad context.

#### Scenario: Finalized activity without grade is flagged
- **WHEN** an activity is marked as completed/finalized for an alumno and no matching calificacion exists
- **THEN** the system SHALL include that entry in potential entregas sin corregir

#### Scenario: Completed activity with grade is not flagged
- **WHEN** an activity is finalized and a matching calificacion exists
- **THEN** the system SHALL NOT include that entry in potential entregas sin corregir

### Requirement: Export potential entregas sin corregir
The system SHALL provide export for potential entregas sin corregir using current filters and tenant scope, returning a downloadable CSV file.

#### Scenario: Export contains filtered rows
- **WHEN** a user requests export with active filters
- **THEN** the exported CSV SHALL include only rows matching those filters

#### Scenario: Export with no matches returns empty dataset
- **WHEN** export is requested and no rows match current filters
- **THEN** the system SHALL return a valid CSV with headers and zero data rows

### Requirement: Require atrasados:ver and tenant scope for export
The detection and export endpoints for potential entregas sin corregir SHALL require `require_permission("atrasados:ver")` and SHALL be restricted to the actor tenant and role-derived scope.

#### Scenario: Cross-tenant rows never exported
- **WHEN** user from tenant A exports potential entregas sin corregir
- **THEN** rows from tenant B SHALL NOT appear in results
