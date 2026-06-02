## 1. Dependencias y configuración

- [x] 1.1 Verificar si `cryptography` está en `pyproject.toml`; si no, agregarla como dependencia
- [x] 1.2 Confirmar que `.env.example` tiene `ENCRYPTION_KEY` documentada con el formato correcto

## 2. Excepciones base (`core/exceptions.py`)

- [x] 2.1 Implementar `AppError(Exception)` como clase base de todas las excepciones de la aplicación
- [x] 2.2 Implementar `NotFoundError(AppError)` (404), `EncryptionError(AppError)` (cifrado), `TenantScopeError(AppError)` (scope de tenant)

## 3. Utilidad AES-256 (`core/security.py`)

- [x] 3.1 Implementar `encrypt_value(plaintext: str) -> str` con AES-256-GCM, nonce aleatorio de 12 bytes, output base64
- [x] 3.2 Implementar `decrypt_value(ciphertext_b64: str) -> str` con verificación GCM tag, raise `EncryptionError` en fallo
- [x] 3.3 Escribir tests de cifrado round-trip, textos idénticos producen ciphertexts distintos, string vacío, descifrado con clave incorrecta

## 4. Modelo Tenant y mixins (`models/`)

- [x] 4.1 Implementar `TimeStampedMixin` (declared_attr) con `created_at` y `updated_at`
- [x] 4.2 Implementar `BaseModelMixin` (declared_attr) con `id` (UUID PK), `tenant_id` (FK → tenant.id), `created_at`, `updated_at`, `deleted_at` (nullable)
- [x] 4.3 Implementar modelo `Tenant` con `id`, `name`, `slug` (unique), `code` (unique), `is_active`, más `TimeStampedMixin` y `deleted_at`
- [x] 4.4 Exportar todos los modelos desde `models/__init__.py` y vincular `target_metadata` en `alembic/env.py`

## 5. Schemas Pydantic (`schemas/`)

- [x] 5.1 Implementar `TenantCreate`, `TenantUpdate`, `TenantResponse` con `extra='forbid'`
- [x] 5.2 Implementar `TenantListParams` para filtros de listado

## 6. Repository genérico (`repositories/`)

- [x] 6.1 Implementar `BaseRepository[ModelT]` con constructor que recibe `session` y `tenant_id`
- [x] 6.2 Implementar `_apply_tenant_scope` y `_apply_soft_delete_filter` como hooks internos
- [x] 6.3 Implementar métodos: `get`, `list`, `paginate`, `create`, `update`, `soft_delete`, `count` con soporte para `include_deleted` y `skip_tenant_scope`
- [x] 6.4 Implementar `TenantRepository` con `get_by_slug` y `get_by_code` (sin tenant-scope)

## 7. Dependencias y tenancy inyección

- [x] 7.1 Completar `core/tenancy.py` con función tenant resolution
- [x] 7.2 Agregar `get_tenant` dependency en `core/dependencies.py` (inyecta tenant_id desde X-Tenant-Slug header)

## 8. Migración Alembic 001

- [x] 8.1 Generar migración `001_tenant.py` con tabla `tenant`, índices únicos en `slug` y `code`, índice en `is_active`
- [x] 8.2 Verificar `alembic upgrade head` contra DB de test ✅ migración 001 ejecutada
- [x] 8.3 Verificar `alembic downgrade -1` revierte correctamente ✅ rollback verificado

## 9. Tests de integración

- [x] 9.1 Safety net: 11/13 C-01 tests pass (2 DB-dependent pre-existing failures)
- [x] 9.2 Test: creación de tenant (escrito — requiere PostgreSQL para ejecución)
- [x] 9.3 Test: aislamiento multi-tenant (escrito — requiere PostgreSQL)
- [x] 9.4 Test: soft delete (escrito — requiere PostgreSQL)
- [x] 9.5 Test: mixin timestamps (escrito — requiere PostgreSQL)
- [x] 9.6 Test: paginación (escrito — requiere PostgreSQL)
- [x] 9.7 Test: skip_tenant_scope (escrito — requiere PostgreSQL)
- [x] 9.8 Test: encrypt/decrypt round-trip ✅ 5/5 PASS
