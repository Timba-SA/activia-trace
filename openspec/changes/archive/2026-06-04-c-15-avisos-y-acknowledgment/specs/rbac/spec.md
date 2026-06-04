## MODIFIED Requirements

### Requirement: System role seed data

The system SHALL seed 7 system roles (`is_system_role = True`) for each tenant created: ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS. Each role SHALL have the permission set defined in `knowledge-base/03_actores_y_roles.md` §3.3, **with the following additions**: COORDINADOR and ADMIN SHALL include `avisos:publicar`. The new permission SHALL be applied in migration 013.

#### Scenario: Seed roles include avisos:publicar for COORDINADOR

- **WHEN** migration 013 is applied and the COORDINADOR role permissions are inspected
- **THEN** the COORDINADOR role SHALL include `avisos:publicar` in addition to its existing permissions

#### Scenario: Seed roles include avisos:publicar for ADMIN

- **WHEN** migration 013 is applied and the ADMIN role permissions are inspected
- **THEN** the ADMIN role SHALL include `avisos:publicar` in addition to its existing permissions

#### Scenario: New permission is created in the permissions table

- **WHEN** migration 013 runs
- **THEN** the permission `avisos:publicar` SHALL exist in the `permission` table
