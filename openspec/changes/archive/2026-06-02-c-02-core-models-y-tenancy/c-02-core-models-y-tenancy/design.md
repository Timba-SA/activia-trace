## Context

activia-trace necesita un cimiento multi-tenant sólido antes de construir cualquier feature de dominio. C-01 dejó el esqueleto FastAPI con configuración, DB, logging y OTel, y reservó placeholders en `core/tenancy.py`, `core/security.py`, `core/exceptions.py`. Este change materializa esos placeholders con: modelo Tenant raíz, mixin base de entidad con UUID + tenant_id + soft delete, repository genérico con tenant-scoping automático, utilidad AES-256 para PII, y la migración 001.

La restricción crítica es que todo lo construido aquí será heredado por CADA entidad del dominio en changes posteriores (C-06, C-07, C-09...). Un error en el mixin, el repository o el cifrado se propaga a todo el sistema.

## Goals / Non-Goals

**Goals:**
- Modelo `Tenant` con UUID PK, slug único, name, code, is_active, timestamps de auditoría.
- Mixin declarativo (`BaseModelMixin`) que toda entidad del dominio usará como base: `id` (UUID, PK), `tenant_id` (FK → Tenant), `created_at`, `updated_at`, `deleted_at` (nullable = soft delete).
- Repositorio genérico (`BaseRepository[ModelT]`) con:
  - CRUD base (get, list, paginate, create, update, soft_delete, hard_delete).
  - Filtro automático de tenant en TODAS las queries (por defecto).
  - Opción `include_deleted=False` para excluir borrados lógicos.
  - Opción `skip_tenant_scope=False` para consultas administrativas (uso explícito, detectable en code review).
- Funciones `encrypt_value` / `decrypt_value` AES-256 usando `ENCRYPTION_KEY` de Settings.
- `Migración 001: tenant` con los índices adecuados.
- Tests: aislamiento multi-tenant, soft delete, cifrado round-trip, mixin timestamps.
- Rellenar `core/tenancy.py` con lógica de resolución de tenant.

**Non-Goals:**
- Auth/JWT (→ C-03). La función `get_tenant` se implementa, pero la obtención del tenant_id desde el JWT se completa en C-03.
- RBAC, permisos, matriz rol×permiso (→ C-04).
- Entidades de dominio (Carrera, Cohorte, Materia → C-06; Usuario → C-07).
- Auditoría (→ C-05).
- Worker de comunicaciones (→ C-12).
- Hard delete físico en operaciones normales (solo admin/repos puede invocar `hard_delete` explícitamente).

## Decisions

### D1 — UUID como PK de Tenant y de todas las entidades

**Decisión**: Usar `uuid.uuid4()` como valor por defecto a nivel de aplicación (no DB). El mixin define `id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)`.

**Alternativa descartada**: `UUID` generado por DB (gen_random_uuid()). Se descarta porque:
- No todas las operaciones pasan por la DB (ej: creación de IDs en memoria para eventos).
- El mixin debe ser independiente del motor de DB.

### D2 — Declarative mixin vs. Base común

**Decisión**: Usar un `declared_attr` mixin separado (`BaseModelMixin`) en lugar de meter todo en `Base`. Razones:
- `Base` en `database.py` debe mantenerse limpio (solo `DeclarativeBase`).
- El mixin se puede componer: si una entidad no necesita soft delete, usa otro mixin.
- Consistencia con el patrón SQLAlchemy 2.0 recomendado.

El modelo `Tenant` NO hereda `BaseModelMixin` (no tiene tenant_id). Hereda directamente de `Base` y agrega sus propios campos + `TimeStampedMixin` (created_at, updated_at) como mixin separado.

### D3 — Tenant scope en Repository: parámetro de instancia vs. contexto global

**Decisión**: Pasar `tenant_id: uuid.UUID` como parámetro en el constructor del repositorio, no como contexto global (thread-local / contextvar).

```
class BaseRepository(Generic[ModelT]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._tenant_id = tenant_id
```

**Alternativa descartada**: Contextvar global que se setea en el middleware. Se descarta porque:
- Rompe la transparencia: el repo depende de un estado externo invisible en la firma.
- Dificulta el testing: requiere mockear el contexto.
- El tenant_id se resuelve en la capa de routing (desde el JWT) y se pasa como dependecy, lo que es explícito y testeable.

### D4 — Soft delete: columna `deleted_at` con filtro default

**Decisión**: Columna `deleted_at: DateTime | None`. Todas las queries del repositorio genérico agregan `WHERE model.deleted_at IS NULL` por defecto.

- `get(id)` → filtra por deleted_at IS NULL, devuelve 404 si está borrado.
- `list()` → filtra por deleted_at IS NULL.
- `soft_delete()` → setea `deleted_at = func.now()`.
- `include_deleted=True` → omite el filtro (para admin/auditoría).
- `hard_delete()` → borrado físico real, SOLO disponible en repositorios específicos (nunca en repositorio genérico por defecto).

### D5 — AES-256: cifrado en `core/security.py` (antes reservado para C-03)

**Decisión**: Adelantar las funciones AES-256 a C-02 (sobrescribiendo el placeholder de `core/security.py`). El resto del módulo (JWT, Argon2id) queda reservado para C-03.

Razón: los atributos `[cifrado]` (DNI, CUIL, CBU, email) se necesitan desde C-07 (usuarios y asignaciones). El cifrado en reposo es un prerrequisito. JWT y Argon2 no.

Función de cifrado:
```
encrypt_value(plaintext: str) -> str
  → genera nonce aleatorio (12 bytes)
  → AES-GCM (modo autenticado)
  → devuelve base64(nonce + ciphertext + tag)

decrypt_value(ciphertext_b64: str) -> str
  → decodifica base64
  → extrae nonce (12 bytes), ciphertext, tag
  → descifra con AES-GCM usando encryption_key
  → si el tag no verifica → raise EncryptionError
```

Key handling: `encryption_key` de Settings (32 bytes exactos). Se codifica a bytes con `.encode()`.

### D6 — Migración 001 con índices

La migración 001 crea la tabla `tenant` con:
- PK: `id` (UUID)
- Unique index: `uix_tenant_slug` (slug)
- Unique index: `uix_tenant_code` (code)
- Index: `ix_tenant_is_active` (para listados por estado)

Las tablas de mixin no se crean aún (son columnas embebidas en cada entidad). La migración 001 solo contiene TENANT.

### D7 — Exceptions base

Crear en `core/exceptions.py`:
- `AppError(Exception)` — base de todas las excepciones de la app.
- `NotFoundError(AppError)` — 404.
- `PermissionDeniedError(AppError)` — 403 (reservado para C-04 pero definido ya).
- `EncryptionError(AppError)` — fallo de cifrado/descifrado.
- `TenantScopeError(AppError)` — cuando se detecta un query sin scope de tenant.

## Risks / Trade-offs

- **Tenant scope en constructor hace el repositorio inmutable por request** → Mitigación: así debe ser. Cada request es un tenant distinto. Si un servicio necesita operar sobre múltiples repos, inyecta el repositorio con el tenant adecuado.
- **AES-GCM nonce de 12 bytes fijo** → Mitigación: tamaño estándar para GCM. Cada cifrado genera un nonce nuevo aleatorio (nunca se reusa). El nonce se almacena junto con el ciphertext.
- **El adelanto de AES-256 a C-02 toca un slot reservado para C-03** → Trade-off aceptado. C-03 no depende de la existencia del cifrado; simplemente reutilizará el módulo. Se actualiza el docstring de `security.py`.
- **Falta de `include_deleted` en queries puede exponer datos borrados** → Mitigación: por defecto el filtro está activo. La opción `include_deleted` está disponible pero requiere intención explícita. Code review debe verificar que no se use innecesariamente.
- **El repository genérico filtra por tenant, pero no por otros scopes (rol, materia)** → Scope adicional es responsabilidad del repositorio específico de cada entidad.

## Migration Plan

1. Crear modelo Tenant y mixin base.
2. Crear repository genérico y repository de Tenant.
3. Crear esquema Pydantic para Tenant.
4. Crear utilidad AES-256.
5. Generar migración 001.
6. Completar `core/tenancy.py`, `core/exceptions.py`.
7. Actualizar `core/dependencies.py` con `get_tenant`.
8. Escribir tests.
9. Ejecutar migración contra DB de test.

Rollback: `alembic downgrade -1` revierte la migración 001.

## Open Questions

- **¿El slug de Tenant debe ser inmutable después de creado?** Se asume que sí (es el identificador lógico del tenant). Si se requiere cambio, se evalúa en C-03 (admin UI).
- **¿Tenant tiene campos de configuración (branding, idioma)?** Se asume que NO en C-02. Se agregan como JSONB o columnas adicionales cuando se implemente la funcionalidad de personalización por tenant.
- **¿`cryptography` o `pycryptodome` para AES-256?** Se recomienda `cryptography` (biblioteca estándar de facto, mantenida, con bindings a OpenSSL). Si no está en pyproject.toml, se agrega.
