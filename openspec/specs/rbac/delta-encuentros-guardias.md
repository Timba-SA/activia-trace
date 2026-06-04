## MODIFIED Requirements

### Requirement: System role seed data

The system SHALL seed 7 system roles (`is_system_role = True`) for each tenant created: ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS. Each role SHALL have the permission set defined in `knowledge-base/03_actores_y_roles.md` §3.3, **with the following additions**: PROFESOR and COORDINADOR SHALL include `encuentros:gestionar`; COORDINADOR and ADMIN SHALL include `encuentros:ver` and `guardias:ver`; TUTOR SHALL include `guardias:registrar`. The new permissions SHALL be applied in migration 011.

#### Scenario: Seed roles include encuentros:gestionar for PROFESOR

- **WHEN** migration 011 is applied and the PROFESOR role permissions are inspected
- **THEN** the PROFESOR role SHALL include `encuentros:gestionar` in addition to its existing permissions

#### Scenario: Seed roles include encuentros:gestionar and encuentros:ver for COORDINADOR

- **WHEN** migration 011 is applied and the COORDINADOR role permissions are inspected
- **THEN** the COORDINADOR role SHALL include `encuentros:gestionar` and `encuentros:ver` in addition to its existing permissions

#### Scenario: Seed roles include encuentros:ver and guardias:ver for ADMIN

- **WHEN** migration 011 is applied and the ADMIN role permissions are inspected
- **THEN** the ADMIN role SHALL include `encuentros:ver` and `guardias:ver` in addition to its existing permissions

#### Scenario: Seed roles include guardias:registrar for TUTOR

- **WHEN** migration 011 is applied and the TUTOR role permissions are inspected
- **THEN** the TUTOR role SHALL include `guardias:registrar` in addition to its existing permissions

#### Scenario: New permissions are created in the permissions table

- **WHEN** migration 011 runs
- **THEN** the permissions `encuentros:gestionar`, `encuentros:ver`, `guardias:registrar`, and `guardias:ver` SHALL exist in the `permission` table
