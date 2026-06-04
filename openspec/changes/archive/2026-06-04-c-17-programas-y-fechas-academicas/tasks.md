## 1. Modelos SQLAlchemy

- [x] 1.1 Crear `backend/app/models/programa_materia.py` con `ProgramaMateria` (BaseModelMixin + FK a Materia, Carrera, Cohorte nullable + titulo, referencia_archivo, contenido_html nullable, version, activo, aprobado_en nullable)
- [x] 1.2 Crear `backend/app/models/fecha_academica.py` con `FechaAcademica` (BaseModelMixin + FK a Materia y Cohorte + tipo enum, numero nullable, fecha, hora nullable, aula nullable, observaciones nullable)

## 2. Schemas Pydantic v2

- [x] 2.1 Crear `backend/app/schemas/programa_materia.py`: `ProgramaMateriaCreate`, `ProgramaMateriaUpdate`, `ProgramaMateriaResponse`, `ProgramaMateriaListResponse`, `GenerarContenidoResponse`. Todos con `extra='forbid'`
- [x] 2.2 Crear `backend/app/schemas/fecha_academica.py`: `FechaAcademicaCreate`, `FechaAcademicaUpdate`, `FechaAcademicaResponse`, `FechaAcademicaListResponse`. Todos con `extra='forbid'`

## 3. Repositories

- [x] 3.1 Crear `backend/app/repositories/programa_materia_repository.py`: `ProgramaMateriaRepository` con CRUD base + list con filtros (materia_id, carrera_id, cohorte_id, activo) + `get_active_for_materia_carrera_cohorte`
- [x] 3.2 Crear `backend/app/repositories/fecha_academica_repository.py`: `FechaAcademicaRepository` con CRUD base + list con filtros (materia_id, cohorte_id, tipo)

## 4. Services

- [x] 4.1 Crear `backend/app/services/programa_materia_service.py`: `ProgramaMateriaService` con métodos `create` (auto-incrementa versión y desactiva anterior), `update`, `deactivate`, `list`, `get_by_id`, `generar_contenido` (genera HTML fragment)
- [x] 4.2 Crear `backend/app/services/fecha_academica_service.py`: `FechaAcademicaService` con CRUD + list con filtros

## 5. Routers

- [x] 5.1 Crear `backend/app/api/v1/routers/programas.py`: endpoints CRUD + `POST /{id}/generar-contenido` con permiso `programas:gestionar` y `programas:ver` para GET
- [x] 5.2 Crear `backend/app/api/v1/routers/fechas_academicas.py`: endpoints CRUD con permiso `programas:gestionar` y `programas:ver` para GET
- [x] 5.3 Registrar ambos routers en `backend/app/api/v1/__init__.py`

## 6. Migración Alembic

- [x] 6.1 Crear `backend/alembic/versions/015_programas_fechas.py` con: tablas `programa_materia`, `fecha_academica` + enum para tipo de fecha + 2 permisos nuevos (`programas:gestionar`, `programas:ver`) + seed en roles COORDINADOR y ADMIN

## 7. Tests

- [x] 7.1 Tests unitarios para `ProgramaMateriaRepository` (CRUD, filtros, versión auto-incremento)
- [x] 7.2 Tests unitarios para `FechaAcademicaRepository` (CRUD, filtros)
- [x] 7.3 Tests de servicio: creación de programa con versionado, desactivación automática de versión anterior
- [x] 7.4 Tests de servicio: generación de contenido HTML a partir de programa activo, 404 si inactivo
- [x] 7.5 Tests de servicio: CRUD de fechas académicas, soft delete
- [x] 7.6 Tests de router: permisos, 403 sin permiso, 422 con datos inválidos
