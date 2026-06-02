## MODIFIED Requirements

### Requirement: System role seed data

The system SHALL seed 7 system roles (`is_system_role = True`) for each tenant created: ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS. Each role SHALL have the permission set defined in `knowledge-base/03_actores_y_roles.md` §3.3, **with the following modifications**: ADMIN SHALL now include `usuarios:asignar` and `usuarios:ver-pii`; COORDINADOR SHALL now include `usuarios:asignar` and `usuarios:ver-pii`. The seed SHALL be applied in migration 005.

#### Scenario: Seed roles include new permissions for ADMIN

- **WHEN** migration 005 is applied and the ADMIN role permissions are inspected for a tenant
- **THEN** the ADMIN role's permissions SHALL include `usuarios:asignar` and `usuarios:ver-pii` in addition to its existing permissions

#### Scenario: Seed roles include new permissions for COORDINADOR

- **WHEN** migration 005 is applied and the COORDINADOR role permissions are inspected for a tenant
- **THEN** the COORDINADOR role's permissions SHALL include `usuarios:asignar` and `usuarios:ver-pii` in addition to its existing permissions

#### Scenario: Migration 005 is idempotent for permission updates

- **WHEN** migration 005 runs against a tenant that already has system roles (from migration 003)
- **THEN** the migration SHALL update existing ADMIN and COORDINADOR roles to include the new permissions without duplicating them

#### Scenario: Seed roles cannot be deleted

- **WHEN** a delete request targets any of the 7 seed roles
- **THEN** the system SHALL return `403 Forbidden` because `is_system_role = True`
