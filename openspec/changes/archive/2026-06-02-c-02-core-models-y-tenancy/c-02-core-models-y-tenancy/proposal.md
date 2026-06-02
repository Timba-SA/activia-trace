## Why

C-01 estableció el esqueleto de la aplicación (FastAPI, DB, Docker, configuración) pero sin modelos de dominio ni aislamiento multi-tenant. Sin un modelo `Tenant` raíz, un mixin base con soft delete, un repository genérico con scope de tenant siempre activo y cifrado AES-256 en reposo, ningún change posterior (auth, RBAC, entidades académicas) puede construirse de forma segura. Este change materializa el cimiento multi-tenant del sistema, dando forma a las decisiones ADR-002 (row-level tenancy) y a la política de soft delete, PII cifrada y migraciones versionadas.

## What Changes

- Crear el modelo **Tenant** (UUID PK, name/slug/code, is_active, timestamps) como raíz del dominio.
- Implementar un **mixin declarativo base** (`TimeStampedBase`) con `id` (UUID), `tenant_id` (FK → Tenant), `created_at`, `updated_at`, `deleted_at` (nullable = soft delete). Todas las entidades del dominio heredarán de este mixin.
- Implementar un **Repository genérico** (`BaseRepository[ModelT]`) que:
  - Auto-filtra toda query por `tenant_id` desde el contexto de sesión.
  - Provee métodos CRUD base (get, list, create, update, soft-delete).
  - Un query sin scope de tenant debe ser detectable (fail en code review).
- Implementar **utilidad de cifrado AES-256** en `core/security.py`:
  - Funciones `encrypt_value(plaintext: str) -> str` y `decrypt_value(ciphertext: str) -> str`.
  - Usa `ENCRYPTION_KEY` de Settings (exactamente 32 bytes).
  - Destinado a atributos `[cifrado]`: DNI, CUIL, CBU, email.
- Crear **Migración 001: tenant** + convención de una migración por cambio de schema.
- Proveer **soft delete transversal**: todo `SELECT` filtra `WHERE deleted_at IS NULL` por defecto; opción `include_deleted` para administración.
- Rellenar los placeholders de C-01 en `core/tenancy.py` y `core/exceptions.py` con lógica real.

## Capabilities

### New Capabilities
- `tenant-model`: Entidad Tenant como raíz del modelo multi-tenant, incluyendo su repositorio y schema Pydantic.
- `base-mixin`: Mixin declarativo SQLAlchemy con id UUID, tenant_id FK, timestamps y soft delete.
- `generic-repository`: Repositorio base CRUD con tenant-scoping automático y soft delete transversal.
- `aes-encryption-at-rest`: Funciones de cifrado/descifrado AES-256 para atributos PII en reposo.
- `alembic-migration-convention`: Setup de migración 001 (tenant) + convención de una migración por cambio de schema.

### Modified Capabilities
- `app-configuration`: Se agrega `ENCRYPTION_KEY` ya fue definida en C-01, pero se refuerza su validación de exactamente 32 caracteres.
- `app-scaffold`: Los placeholders `core/tenancy.py`, `core/security.py`, `core/exceptions.py`, `core/dependencies.py` se completan con lógica real.

## Impact

- `backend/app/core/tenancy.py` → se completa con lógica de resolución de tenant.
- `backend/app/core/security.py` → se completa con funciones AES-256 (antes reservado para C-03, pero AES se adelanta a C-02 porque es necesario para atributos `[cifrado]` desde C-07).
- `backend/app/core/exceptions.py` → se completa con excepciones de dominio base.
- `backend/app/core/dependencies.py` → se agrega `get_tenant` dependency.
- `backend/app/models/` → se crea `tenant.py` y `base.py` (mixin).
- `backend/app/repositories/` → se crea `base.py` (repository genérico) y `tenant.py`.
- `backend/app/schemas/` → se crea `tenant.py`.
- `backend/alembic/` → se crea `versions/001_tenant.py`.
- `backend/tests/` → nuevos tests para tenant, mixin, repository, cifrado.
- `backend/pyproject.toml` → posible nueva dependencia para `cryptography` si no está ya declarada.
