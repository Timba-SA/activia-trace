## MODIFIED Requirements

### Requirement: System role seed data

The system SHALL seed 7 system roles (`is_system_role = True`) for each tenant created: ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS. Each role SHALL have the permission set defined in `knowledge-base/03_actores_y_roles.md` §3.3, **with the following additions**: PROFESOR, COORDINADOR and ADMIN SHALL include `tareas:gestionar`. The new permission SHALL be applied in migration 014.

#### Scenario: Seed roles include tareas:gestionar for PROFESOR

- **WHEN** migration 014 is applied and the PROFESOR role permissions are inspected
- **THEN** the PROFESOR role SHALL include `tareas:gestionar` in addition to its existing permissions

#### Scenario: Seed roles include tareas:gestionar for COORDINADOR

- **WHEN** migration 014 is applied and the COORDINADOR role permissions are inspected
- **THEN** the COORDINADOR role SHALL include `tareas:gestionar` in addition to its existing permissions

#### Scenario: Seed roles include tareas:gestionar for ADMIN

- **WHEN** migration 014 is applied and the ADMIN role permissions are inspected
- **THEN** the ADMIN role SHALL include `tareas:gestionar` in addition to its existing permissions

#### Scenario: New permission is created in the permissions table

- **WHEN** migration 014 runs
- **THEN** the permission `tareas:gestionar` SHALL exist in the `permission` table
