## MODIFIED Requirements

### Requirement: System role seed data

The system SHALL seed 7 system roles (`is_system_role = True`) for each tenant created: ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS. Each role SHALL have the permission set defined in `knowledge-base/03_actores_y_roles.md` §3.3, **with the following modifications**: ADMIN SHALL now include `usuarios:asignar`, `usuarios:ver-pii`, `avisos:publicar`, `tareas:gestionar`, `programas:gestionar`, and `programas:ver`; COORDINADOR SHALL now include `usuarios:asignar`, `usuarios:ver-pii`, `avisos:publicar`, `tareas:gestionar`, `programas:gestionar`, and `programas:ver`; PROFESOR SHALL now include `tareas:gestionar`. The seed modifications were applied incrementally: `usuarios:asignar` and `usuarios:ver-pii` in migration 005; `avisos:publicar` in migration 013; `tareas:gestionar` for PROFESOR, COORDINADOR, and ADMIN in migration 014; `programas:gestionar` and `programas:ver` for COORDINADOR and ADMIN in migration 015.

#### Scenario: Seed roles include programas:gestionar and programas:ver for COORDINADOR (migration 015)

- **WHEN** migration 015 is applied and the COORDINADOR role permissions are inspected
- **THEN** the COORDINADOR role SHALL include `programas:gestionar` and `programas:ver` in addition to its existing permissions

#### Scenario: Seed roles include programas:gestionar and programas:ver for ADMIN (migration 015)

- **WHEN** migration 015 is applied and the ADMIN role permissions are inspected
- **THEN** the ADMIN role SHALL include `programas:gestionar` and `programas:ver` in addition to its existing permissions

#### Scenario: New permissions are created in the permissions table (migration 015)

- **WHEN** migration 015 runs
- **THEN** the permissions `programas:gestionar` and `programas:ver` SHALL exist in the `permission` table
