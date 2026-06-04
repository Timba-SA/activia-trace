## Why

El modelo `Asignacion` ya existe (C-07) con CRUD básico, pero los equipos docentes requieren operaciones de alto nivel que el CRUD no cubre: vista contextual por docente, asignación masiva, clonado entre períodos, modificación de vigencia en bloque y exportación. Sin esto, cada inicio de cuatrimestre requiere reasignar manualmente decenas de docentes materia por materia.

## What Changes

- Nueva permiso `equipos:asignar` para COORDINADOR y ADMIN (operaciones de escritura); `equipos:ver` para lecturas
- Nuevo router `/api/equipos` con endpoints para:
  - **F4.2** — `GET /api/equipos/mis-equipos`: vista propia del docente (PROFESOR, TUTOR, NEXO, COORDINADOR)
  - **F4.3** — `GET /api/equipos`: listado completo de asignaciones del tenant con filtros (COORDINADOR, ADMIN)
  - **F4.4** — `POST /api/equipos/asignacion-masiva`: creación en bloque de asignaciones
  - **F4.5** — `POST /api/equipos/clonar`: duplica equipo entre cohortes
  - **F4.6** — `PATCH /api/equipos/vigencia`: actualiza desde/hasta de todo un equipo
  - **F4.7** — `GET /api/equipos/exportar`: descarga CSV con detalle del equipo
- Nuevos schemas Pydantic para bulk create, clone request, vigencia update
- Nuevos métodos en `AsignacionService` y `AsignacionRepository`
- Seed del permiso `equipos:asignar` en `COORDINADOR` y `ADMIN`

## Capabilities

### New Capabilities
- `equipos-vista`: Endpoints GET de consulta — mis equipos (F4.2) y listado completo del tenant (F4.3)
- `equipos-gestion`: Endpoints POST/PATCH/GET de escritura — asignación masiva (F4.4), clonado (F4.5), vigencia (F4.6), exportación (F4.7)

### Modified Capabilities
- `usuarios-y-asignaciones`: no se modifican requirements existentes; se agregan como delta specs en `equipos-vista` y `equipos-gestion`

## Impact

- `backend/app/api/v1/routers/equipos.py` — nuevo router (~200 LOC)
- `backend/app/repositories/asignacion_repository.py` — nuevos métodos: `list_with_filters`, `bulk_create`, `update_vigencia_by_team`
- `backend/app/services/asignacion_service.py` — nuevos métodos: `mis_equipos`, `list_equipos`, `asignacion_masiva`, `clonar`, `update_vigencia_equipo`, `exportar_equipo`
- `backend/app/schemas/asignacion.py` — nuevos schemas: `AsignacionMasivaRequest`, `CloneRequest`, `VigenciaUpdateRequest`
- Seed data para `equipos:asignar` en roles COORDINADOR y ADMIN
- `backend/app/main.py` — registro del nuevo router
