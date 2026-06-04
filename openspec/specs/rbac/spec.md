## MODIFIED Requirements

### Requirement: System role seed data

The system SHALL seed 7 system roles (`is_system_role = True`) for each tenant created: ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS. Each role SHALL have the permission set defined in `knowledge-base/03_actores_y_roles.md` §3.3, **with the following modifications**: ADMIN SHALL now include `usuarios:asignar`, `usuarios:ver-pii`, `avisos:publicar`, `tareas:gestionar`, `programas:gestionar`, and `programas:ver`; COORDINADOR SHALL now include `usuarios:asignar`, `usuarios:ver-pii`, `avisos:publicar`, `tareas:gestionar`, `programas:gestionar`, and `programas:ver`; PROFESOR SHALL now include `tareas:gestionar`. The seed modifications were applied incrementally: `usuarios:asignar` and `usuarios:ver-pii` in migration 005; `avisos:publicar` in migration 013; `tareas:gestionar` for PROFESOR, COORDINADOR, and ADMIN in migration 014; `programas:gestionar` and `programas:ver` for COORDINADOR and ADMIN in migration 015.

#### Scenario: Seed roles include new permissions for ADMIN

- **WHEN** migration 005 is applied and the ADMIN role permissions are inspected for a tenant
- **THEN** the ADMIN role's permissions SHALL include `usuarios:asignar` and `usuarios:ver-pii` in addition to its existing permissions

#### Scenario: Seed roles include new permissions for COORDINADOR

- **WHEN** migration 005 is applied and the COORDINADOR role permissions are inspected for a tenant
- **THEN** the COORDINADOR role's permissions SHALL include `usuarios:asignar` and `usuarios:ver-pii` in addition to its existing permissions

#### Scenario: Migration 005 is idempotent for permission updates

- **WHEN** migration 005 runs against a tenant that already has system roles (from migration 003)
- **THEN** the migration SHALL update existing ADMIN and COORDINADOR roles to include the new permissions without duplicating them

#### Scenario: Seed roles include avisos:publicar for COORDINADOR (migration 013)

- **WHEN** migration 013 is applied and the COORDINADOR role permissions are inspected
- **THEN** the COORDINADOR role SHALL include `avisos:publicar` in addition to its existing permissions

#### Scenario: Seed roles include avisos:publicar for ADMIN (migration 013)

- **WHEN** migration 013 is applied and the ADMIN role permissions are inspected
- **THEN** the ADMIN role SHALL include `avisos:publicar` in addition to its existing permissions

#### Scenario: New avisos:publicar permission is created (migration 013)

- **WHEN** migration 013 runs
- **THEN** the permission `avisos:publicar` SHALL exist in the `permission` table

#### Scenario: Seed roles include tareas:gestionar for PROFESOR (migration 014)

- **WHEN** migration 014 is applied and the PROFESOR role permissions are inspected
- **THEN** the PROFESOR role SHALL include `tareas:gestionar` in addition to its existing permissions

#### Scenario: Seed roles include tareas:gestionar for COORDINADOR (migration 014)

- **WHEN** migration 014 is applied and the COORDINADOR role permissions are inspected
- **THEN** the COORDINADOR role SHALL include `tareas:gestionar` in addition to its existing permissions

#### Scenario: Seed roles include tareas:gestionar for ADMIN (migration 014)

- **WHEN** migration 014 is applied and the ADMIN role permissions are inspected
- **THEN** the ADMIN role SHALL include `tareas:gestionar` in addition to its existing permissions

#### Scenario: New permission is created in the permissions table (migration 014)

- **WHEN** migration 014 runs
- **THEN** the permission `tareas:gestionar` SHALL exist in the `permission` table

#### Scenario: Seed roles cannot be deleted

- **WHEN** a delete request targets any of the 7 seed roles
- **THEN** the system SHALL return `403 Forbidden` because `is_system_role = True`

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

#### Scenario: Seed roles include programas:gestionar and programas:ver for COORDINADOR (migration 015)

- **WHEN** migration 015 is applied and the COORDINADOR role permissions are inspected
- **THEN** the COORDINADOR role SHALL include `programas:gestionar` and `programas:ver` in addition to its existing permissions

#### Scenario: Seed roles include programas:gestionar and programas:ver for ADMIN (migration 015)

- **WHEN** migration 015 is applied and the ADMIN role permissions are inspected
- **THEN** the ADMIN role SHALL include `programas:gestionar` and `programas:ver` in addition to its existing permissions

#### Scenario: New permissions are created in the permissions table (migration 015)

- **WHEN** migration 015 runs
- **THEN** the permissions `programas:gestionar` and `programas:ver` SHALL exist in the `permission` table
