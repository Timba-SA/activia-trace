## ADDED Requirements

### Requirement: Repository genérico con tenant-scoping automático

El sistema SHALL proveer una clase `BaseRepository[ModelT: BaseModelMixin]` que implemente operaciones CRUD base con scoping automático de tenant. El constructor SHALL recibir `session: AsyncSession` y `tenant_id: uuid.UUID`. Cada método que acceda a la DB SHALL filtrar por `tenant_id` por defecto mediante un hook interno `_apply_tenant_scope`.

#### Scenario: Filtro automático de tenant en get

- **WHEN** se invoca `repo.get(record_id)` donde el registro existe pero pertenece a otro tenant
- **THEN** se retorna `None` (el registro no es visible)

#### Scenario: Filtro automático de tenant en list

- **WHEN** se invoca `repo.list()`
- **THEN** solo se retornan registros con `tenant_id` igual al del repositorio

#### Scenario: Inserción con tenant_id automático

- **WHEN** se invoca `repo.create(data)` donde `data` no incluye `tenant_id`
- **THEN** el repositorio asigna automáticamente el `tenant_id` del constructor al modelo antes de persistir

### Requirement: Soft delete transversal en repository

Todos los métodos `get`, `list` del repositorio genérico SHALL filtrar por `deleted_at IS NULL` por defecto. El método `soft_delete` SHALL setear `deleted_at = func.now()`.

#### Scenario: Soft delete oculta el registro

- **WHEN** se invoca `repo.soft_delete(record_id)` y luego `repo.get(record_id)`
- **THEN** el registro no es encontrado (retorna None)

#### Scenario: include_deleted revela registros borrados

- **WHEN** se invoca `repo.get(record_id, include_deleted=True)`
- **THEN** se retorna el registro incluso si tiene `deleted_at` no nulo

#### Scenario: list con include_deleted

- **WHEN** se invoca `repo.list(include_deleted=True)`
- **THEN** se retornan todos los registros del tenant, incluyendo los soft-deleteados

### Requirement: Skip tenant scope para consultas administrativas

El sistema SHALL proveer un método o flag `skip_tenant_scope` que permita omitir el filtro de tenant. Su uso SHALL ser explícito y detectable en code review. Si se usa sin necesidad, se considera un bug.

#### Scenario: Skip tenant scope explícito

- **WHEN** se invoca `repo.list(skip_tenant_scope=True)`
- **THEN** se retornan registros de TODOS los tenants

### Requirement: Métodos CRUD base

El repositorio genérico SHALL exponer al menos los siguientes métodos: `get(id, include_deleted=False) → ModelT | None`, `list(*filters, include_deleted=False, skip_tenant_scope=False, **kwargs) → list[ModelT]`, `paginate(page, per_page, *filters, include_deleted=False) → Page[ModelT]`, `create(data: dict | BaseModel) → ModelT`, `update(id, data: dict | BaseModel) → ModelT`, `soft_delete(id) → None`, `count(*filters, include_deleted=False) → int`.

#### Scenario: Paginación con tenant scope

- **WHEN** se invoca `repo.paginate(page=1, per_page=10)`
- **THEN** se retorna una página con solo los registros del tenant activo, respetando los límites de paginación
