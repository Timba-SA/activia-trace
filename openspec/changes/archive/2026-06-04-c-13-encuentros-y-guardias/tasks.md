## 1. Modelos SQLAlchemy

- [x] 1.1 Crear `backend/app/models/encuentro_slot.py` con `SlotEncuentro` (BaseModelMixin + FK a Asignacion y Materia)
- [x] 1.2 Crear `backend/app/models/encuentro_instancia.py` con `InstanciaEncuentro` (BaseModelMixin + FK a Materia, slot_id nullable)
- [x] 1.3 Crear `backend/app/models/guardia.py` con `Guardia` (BaseModelMixin + FKs a Asignacion, Materia, Carrera, Cohorte; sin soft delete por ahora)

## 2. Schemas Pydantic v2

- [x] 2.1 Crear `backend/app/schemas/encuentro.py`: `SlotEncuentroCreate`, `SlotEncuentroUpdate`, `SlotEncuentroResponse`, `InstanciaEncuentroCreate`, `InstanciaEncuentroUpdate`, `InstanciaEncuentroResponse`, list responses. Todos con `extra='forbid'`
- [x] 2.2 Crear `backend/app/schemas/guardia.py`: `GuardiaCreate`, `GuardiaUpdate` (solo estado), `GuardiaResponse`, list response. Todos con `extra='forbid'`

## 3. Repositories

- [x] 3.1 Crear `backend/app/repositories/encuentro_repository.py`: `SlotEncuentroRepository` (CRUD base + list por materia/asignacion) e `InstanciaEncuentroRepository` (list por slot, list con filtros admin, list futuras para export)
- [x] 3.2 Crear `backend/app/repositories/guardia_repository.py`: `GuardiaRepository` (list por usuario, list con filtros admin, bulk para export)

## 4. Services

- [x] 4.1 Crear `backend/app/services/encuentro_service.py`: `EncuentroService` con métodos `create_slot` (genera N instancias), `create_instancia_independiente`, `update_instancia`, `list_slots`, `list_instancias_por_slot`, `list_instancias_admin`, `exportar_html`
- [x] 4.2 Crear `backend/app/services/guardia_service.py`: `GuardiaService` con `create`, `update_estado`, `list_mis_guardias`, `list_guardias_admin`, `exportar_csv`

## 5. Routers

- [x] 5.1 Crear `backend/app/api/v1/routers/encuentros.py`: endpoints para slots e instancias con permisos `encuentros:gestionar` y `encuentros:ver`
- [x] 5.2 Crear `backend/app/api/v1/routers/guardias.py`: endpoints para guardias con permisos `guardias:registrar` y `guardias:ver`
- [x] 5.3 Registrar ambos routers en `backend/app/api/v1/__init__.py`

## 6. Migración Alembic

- [x] 6.1 Crear `backend/alembic/versions/011_encuentros_guardias.py` con: tablas `slot_encuentro`, `instancia_encuentro`, `guardia` + enum types + 4 permisos nuevos + seed en roles PROFESOR, COORDINADOR, ADMIN, TUTOR

## 7. Tests

- [x] 7.1 Tests unitarios para `SlotEncuentroRepository` e `InstanciaEncuentroRepository`
- [x] 7.2 Tests unitarios para `GuardiaRepository`
- [x] 7.3 Tests de servicio: creación de slot recurrente genera N instancias, validaciones mutuamente excluyentes, límite de semanas
- [x] 7.4 Tests de servicio: CRUD de instancias independientes, actualización de estado
- [x] 7.5 Tests de servicio: registro y consulta de guardias, restricción de modificación post-finalización
- [x] 7.6 Tests de exportación: HTML de encuentros, CSV de guardias
- [x] 7.7 Tests de router: permisos, 403 sin permiso, 422 con datos inválidos
