## 1. Models

- [x] 1.1 Create `Carrera` model in `backend/app/models/carrera.py` extending `Base, BaseModelMixin`: id, tenant_id, codigo, nombre, descripcion (nullable), duracion_anios (nullable, int), is_active (bool, default True), timestamps, soft delete
- [x] 1.2 Create `Cohorte` model in `backend/app/models/cohorte.py` extending `Base, BaseModelMixin`: id, tenant_id, carrera_id (FK, not nullable), nombre, anio (int), is_active (bool, default True), timestamps, soft delete
- [x] 1.3 Create `Materia` model in `backend/app/models/materia.py` extending `Base, BaseModelMixin`: id, tenant_id, carrera_id (FK, nullable), codigo, nombre, descripcion (nullable), carga_horaria (nullable, int), is_active (bool, default True), timestamps, soft delete

## 2. Schemas

- [x] 2.1 Create `schemas/carrera.py` with CarreraCreate, CarreraUpdate, CarreraResponse, CarreraListResponse (all with `extra='forbid'`)
- [x] 2.2 Create `schemas/cohorte.py` with CohorteCreate, CohorteUpdate, CohorteResponse, CohorteListResponse (all with `extra='forbid'`)
- [x] 2.3 Create `schemas/materia.py` with MateriaCreate, MateriaUpdate, MateriaResponse, MateriaListResponse (all with `extra='forbid'`)

## 3. Repositories

- [x] 3.1 Create `CarreraRepository` in `backend/app/repositories/carrera_repository.py` extending `BaseRepository[Carrera]` with `get_by_codigo()` method
- [x] 3.2 Create `CohorteRepository` in `backend/app/repositories/cohorte_repository.py` extending `BaseRepository[Cohorte]` with `get_by_nombre_and_carrera()` method and `count_by_carrera()` for delete protection
- [x] 3.3 Create `MateriaRepository` in `backend/app/repositories/materia_repository.py` extending `BaseRepository[Materia]` with `get_by_codigo()` method

## 4. Service

- [x] 4.1 Create `backend/app/services/estructura_service.py` with CarreraService, CohorteService, MateriaService classes encapsulating:
  - Create/update/delete operations
  - Uniqueness checks before create/update
  - Business rule: cannot create cohorte for inactive carrera
  - Business rule: cannot soft-delete carrera with non-deleted cohorts
  - Business rule: carrera_id FK validation on create

## 5. Routers

- [x] 5.1 Create `routers/carreras.py` with endpoints for list (paginated), get by id, create, update, soft delete under prefix `/api/admin/carreras`
- [x] 5.2 Create `routers/cohortes.py` with endpoints for list (paginated, filterable by carrera_id), get by id, create, update, soft delete under prefix `/api/admin/cohortes`
- [x] 5.3 Create `routers/materias.py` with endpoints for list (paginated, filterable by carrera_id), get by id, create, update, soft delete under prefix `/api/admin/materias`
- [x] 5.4 Register all three routers in `backend/app/main.py`

## 6. Alembic Migration

- [x] 6.1 Generate migration `004_estructura_academica.py` with:
  - Create `carrera` table
  - Create `cohorte` table with FK → carrera
  - Create `materia` table with nullable FK → carrera
  - Unique constraints: `uk_carrera_codigo_tenant` on (tenant_id, codigo), `uk_cohorte_nombre_carrera_tenant` on (tenant_id, carrera_id, nombre), `uk_materia_codigo_tenant` on (tenant_id, codigo)
  - Indexes on FK columns and is_active

## 7. Tests

- [x] 7.1 Write tests for Carrera CRUD: create, get, list, update, soft delete, duplicate codigo per tenant, multi-tenant isolation, delete with cohorts guard
- [x] 7.2 Write tests for Cohorte CRUD: create, get, list, update, soft delete, duplicate nombre per carrera, inactive carrera guard
- [x] 7.3 Write tests for Materia CRUD: create, get, list, update, soft delete, duplicate codigo per tenant, multi-tenant isolation, nullable carrera_id
- [x] 7.4 Write tests for permission guard: authorized user passes, unauthorized user gets 403
