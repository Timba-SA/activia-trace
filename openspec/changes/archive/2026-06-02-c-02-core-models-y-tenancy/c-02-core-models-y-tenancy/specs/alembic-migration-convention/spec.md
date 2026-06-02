## ADDED Requirements

### Requirement: Una migración Alembic por cambio de schema

El sistema SHALL seguir la convención de una migración Alembic por cambio de schema. Cada cambio estructural (nueva tabla, columna, índice, FK, constraint) SHALL generar una nueva revisión de migración. No se SHALL acumular múltiples cambios de schema no relacionados en una misma migración.

#### Scenario: Migración 001 crea tabla tenant

- **WHEN** se ejecuta `alembic upgrade head`
- **THEN** la tabla `tenant` existe con columnas: `id` (UUID, PK), `name` (text, NOT NULL), `slug` (text, NOT NULL, UNIQUE), `code` (text, NOT NULL, UNIQUE), `is_active` (boolean, default true), `created_at` (datetime, NOT NULL), `updated_at` (datetime, NOT NULL), `deleted_at` (datetime, nullable)

#### Scenario: Rollback de migración 001

- **WHEN** se ejecuta `alembic downgrade -1`
- **THEN** la tabla `tenant` se elimina

### Requirement: Naming convention para migraciones

Cada archivo de migración SHALL seguir el formato `NNNN_description.py` donde `NNNN` es el número de revisión secuencial (001, 002, 003...) y `description` es un snake_case corto que describa el contenido. Ejemplo: `001_tenant.py`.

#### Scenario: Convención de nomenclatura

- **WHEN** se inspecciona `alembic/versions/`
- **THEN** los archivos de migración siguen el formato `NNNN_description.py`

### Requirement: Índices en migración 001

La migración 001 SHALL crear los siguientes índices sobre `tenant`: índice único sobre `slug` (`uix_tenant_slug`), índice único sobre `code` (`uix_tenant_code`), índice sobre `is_active` (`ix_tenant_is_active`).

#### Scenario: Índices de tenant existen

- **WHEN** se inspeccionan los índices de la tabla `tenant`
- **THEN** existen `uix_tenant_slug`, `uix_tenant_code` e `ix_tenant_is_active`
