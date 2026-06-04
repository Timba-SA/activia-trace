## ADDED Requirements

### Requirement: Docente visualiza sus equipos (F4.2)

El sistema SHALL exponer un endpoint `GET /api/equipos/mis-equipos` que retorne las asignaciones activas del usuario autenticado con rol docente (PROFESOR, TUTOR, NEXO, COORDINADOR). Cada asignación SHALL incluir: rol, carrera, materia, cohorte, comisiones, vigencia (desde/hasta), estado (vigente/vencida). La respuesta SHALL estar paginada con `limit` y `offset`.

#### Scenario: Docente ve sus equipos con filtro por estado

- **WHEN** un usuario con rol PROFESOR envía GET a `/api/equipos/mis-equipos?estado=vigente`
- **THEN** el sistema SHALL retornar solo las asignaciones activas del usuario donde la fecha actual está dentro del rango `fecha_inicio`–`fecha_fin`

#### Scenario: Docente ve sus equipos filtrado por materia

- **WHEN** un usuario con rol TUTOR envía GET a `/api/equipos/mis-equipos?materia_id=<uuid>`
- **THEN** el sistema SHALL retornar solo las asignaciones del usuario para esa materia

#### Scenario: Docente ve sus equipos con múltiples filtros combinados

- **WHEN** un usuario con rol COORDINADOR envía GET a `/api/equipos/mis-equipos?rol=PROFESOR&carrera_id=<uuid>&cohorte_id=<uuid>`
- **THEN** el sistema SHALL retornar solo las asignaciones del usuario que coinciden con todos los filtros

#### Scenario: Docente sin asignaciones recibe lista vacía

- **WHEN** un usuario sin asignaciones envía GET a `/api/equipos/mis-equipos`
- **THEN** el sistema SHALL retornar `{ "items": [], "total": 0, "pages": 0 }`

#### Scenario: Profesor sin rol docente recibe 403

- **WHEN** un usuario con rol ALUMNO envía GET a `/api/equipos/mis-equipos`
- **THEN** el sistema SHALL retornar `403 Forbidden` (no tiene `equipos:ver`)

#### Scenario: Mis equipos retorna paginación

- **WHEN** un docente envía GET a `/api/equipos/mis-equipos?limit=10&offset=20`
- **THEN** el sistema SHALL retornar como máximo 10 items comenzando desde el registro 21, con `total` y `pages`

### Requirement: COORDINADOR/ADMIN listan todas las asignaciones del tenant (F4.3)

El sistema SHALL exponer un endpoint `GET /api/equipos` que retorne todas las asignaciones activas (no soft-deleted) del tenant actual, con filtros por `materia_id`, `carrera_id`, `cohorte_id`, `usuario_id`, `nombre` (búsqueda textual sobre nombre/apellido del usuario asignado), `rol`, y `responsable_id`. El guard SHALL ser `equipos:ver`.

#### Scenario: Listado de equipos filtrado por materia y carrera

- **WHEN** un COORDINADOR envía GET a `/api/equipos?materia_id=<uuid>&carrera_id=<uuid>`
- **THEN** el sistema SHALL retornar asignaciones que coinciden con ambos filtros

#### Scenario: Listado de equipos filtrado por nombre de docente

- **WHEN** un ADMIN envía GET a `/api/equipos?nombre=Garcia`
- **THEN** el sistema SHALL retornar asignaciones cuyo usuario asociado tenga "Garcia" en `nombre` o `apellido` (case-insensitive partial match)

#### Scenario: Listado de equipos sin filtros retorna todas las asignaciones activas del tenant

- **WHEN** un COORDINADOR envía GET a `/api/equipos`
- **THEN** el sistema SHALL retornar todas las asignaciones activas del tenant, paginadas

#### Scenario: Usuario sin equipos:ver recibe 403

- **WHEN** un usuario sin permiso `equipos:ver` envía GET a `/api/equipos`
- **THEN** el sistema SHALL retornar `403 Forbidden`

#### Scenario: Listado de equipos aísla por tenant

- **WHEN** un COORDINADOR del tenant A consulta `/api/equipos`
- **THEN** el sistema SHALL retornar solo asignaciones del tenant A (ninguna del tenant B)
