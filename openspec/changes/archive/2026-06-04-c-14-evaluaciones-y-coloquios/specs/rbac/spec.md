## ADDED Requirements

### Requirement: Coloquios permissions added to seed

The system SHALL include 3 new permissions in the RBAC seed: `coloquios:gestionar` (COORDINADOR, ADMIN), `coloquios:ver` (COORDINADOR, ADMIN), `coloquios:reservar` (ALUMNO). These SHALL be added in the next migration after the `coloquios` models are created.

#### Scenario: ADMIN role includes coloquios:gestionar and coloquios:ver

- **WHEN** the migration is applied and the ADMIN role permissions are inspected
- **THEN** the ADMIN role SHALL include `coloquios:gestionar` and `coloquios:ver` in its permission set

#### Scenario: COORDINADOR role includes coloquios:gestionar and coloquios:ver

- **WHEN** the migration is applied and the COORDINADOR role permissions are inspected
- **THEN** the COORDINADOR role SHALL include `coloquios:gestionar` and `coloquios:ver` in its permission set

#### Scenario: ALUMNO role includes coloquios:reservar

- **WHEN** the migration is applied and the ALUMNO role permissions are inspected
- **THEN** the ALUMNO role SHALL include `coloquios:reservar` in its permission set
