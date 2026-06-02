## ADDED Requirements

### Requirement: Modelo Tenant como raíz del multi-tenancy

El sistema SHALL modelar la entidad `Tenant` como raíz del modelo multi-tenant. Cada institución educativa es un tenant. El modelo SHALL contener: `id` (UUID, PK), `name` (texto, nombre de la institución), `slug` (texto, identificador URL-friendly único), `code` (texto, código corto interno único), `is_active` (booleano, default true), `created_at` (datetime, server default), `updated_at` (datetime, on update). Todos los tenants tienen soft delete habilitado (`deleted_at` nullable).

#### Scenario: Creación de tenant exitosa

- **WHEN** se crea un tenant con name, slug y code válidos
- **THEN** el tenant se persiste con `id` UUID, `created_at` y `updated_at` generados automáticamente, `is_active = true`, y `deleted_at = NULL`

#### Scenario: Slug único a nivel global

- **WHEN** se intenta crear un segundo tenant con el mismo `slug`
- **THEN** la operación falla con error de unicidad (constraint `uix_tenant_slug`)

#### Scenario: Code único a nivel global

- **WHEN** se intenta crear un segundo tenant con el mismo `code`
- **THEN** la operación falla con error de unicidad (constraint `uix_tenant_code`)

#### Scenario: Tenant inactivo

- **WHEN** se crea un tenant con `is_active = false`
- **THEN** el tenant se persiste correctamente pero no se muestra en listados por defecto

#### Scenario: Listado de tenants activos

- **WHEN** se listan tenants con filtro activo
- **THEN** solo se retornan aquellos con `is_active = true` y `deleted_at IS NULL`

### Requirement: Esquema Pydantic para Tenant

El sistema SHALL exponer un schema Pydantic `TenantCreate` con campos `name`, `slug`, `code`, `is_active` (opcional), y `TenantResponse` con todos los campos del modelo. Los schemas SHALL usar `extra='forbid'`.

#### Scenario: Creación con campos extra

- **WHEN** se envía un payload con campos no declarados en `TenantCreate`
- **THEN** la validación falla con error 422

### Requirement: Repositorio de Tenant

El sistema SHALL proveer un `TenantRepository` que herede de `BaseRepository[TenantModel]` y agregue métodos de búsqueda por slug (`get_by_slug`) y por code (`get_by_code`). Dado que Tenant es la entidad raíz, el repositorio de Tenant NO aplica tenant-scoping (no tiene tenant_id propio).

#### Scenario: Búsqueda por slug

- **WHEN** se busca un tenant por slug existente
- **THEN** se retorna el tenant correspondiente

#### Scenario: Búsqueda por slug inexistente

- **WHEN** se busca un tenant por slug que no existe
- **THEN** se retorna `None`
