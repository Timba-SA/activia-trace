## ADDED Requirements

### Requirement: Mixin base con UUID, tenant_id, timestamps y soft delete

El sistema SHALL proveer un mixin declarativo SQLAlchemy (`BaseModelMixin`) que todas las entidades del dominio (excepto Tenant) hereden. El mixin SHALL definir: `id` (UUID, PK, default uuid4), `tenant_id` (UUID, FK → Tenant, NOT NULL), `created_at` (DateTime, server_default = func.now()), `updated_at` (DateTime, onupdate = func.now()), `deleted_at` (DateTime, nullable, default None). El mixin SHALL ser un `MappedAsDataclass` o `declared_attr` para permitir herencia múltiple con `Base`.

#### Scenario: Creación de entidad con mixin

- **WHEN** se crea una instancia de una entidad que hereda de `BaseModelMixin`
- **THEN** se generan `id` (UUID aleatorio), `created_at` y `updated_at` automáticamente; `deleted_at` es NULL

#### Scenario: Actualización de timestamp

- **WHEN** se modifica un registro de una entidad con mixin
- **THEN** `updated_at` se actualiza automáticamente al momento de la modificación

#### Scenario: Soft delete por defecto

- **WHEN** se elimina lógicamente un registro (soft delete)
- **THEN** `deleted_at` se setea al momento actual; el registro persiste en la DB

#### Scenario: Mixin generador de columnas vía declared_attr

- **WHEN** se inspecciona una entidad que hereda del mixin
- **THEN** las columnas `id`, `tenant_id`, `created_at`, `updated_at`, `deleted_at` existen como columnas propias de la tabla (no como columnas compartidas)

### Requirement: Mixin separado para timestamps (sin tenant_id)

El sistema SHALL proveer un segundo mixin `TimeStampedMixin` con solo `created_at` y `updated_at`, sin `tenant_id` ni `deleted_at`. Este mixin se usa para entidades que no pertenecen a un tenant (como la propia entidad Tenant).

#### Scenario: TimeStampedMixin en Tenant

- **WHEN** se define el modelo Tenant usando `TimeStampedMixin`
- **THEN** Tenant tiene `created_at` y `updated_at` pero no `tenant_id` ni `deleted_at`

### Requirement: FK constraint a Tenant

El campo `tenant_id` del mixin SHALL definir una foreign key explícita a `tenant.id` con `ondelete=CASCADE`.

#### Scenario: Eliminación de tenant en cascada

- **WHEN** se elimina un tenant (soft delete)
- **THEN** ninguna entidad se elimina físicamente en cascada; el soft delete deja los registros existentes con `deleted_at` seteados (FK se mantiene)
