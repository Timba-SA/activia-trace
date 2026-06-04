## ADDED Requirements

### Requirement: Asignación masiva de docentes (F4.4)

El sistema SHALL exponer un endpoint `POST /api/equipos/asignacion-masiva` que reciba una lista de `usuario_id`, un contexto académico común (`materia_id`, `carrera_id`, `cohorte_id`, `rol`) y una vigencia (`fecha_inicio`, `fecha_fin`), y cree todas las asignaciones en una sola transacción. Si algún usuario no existe, la operación SHALL fallar completamente (rollback). Guard: `equipos:asignar`. Estado HTTP: `201 Created`.

#### Scenario: Asignación masiva exitosa

- **WHEN** un COORDINADOR envía POST a `/api/equipos/asignacion-masiva` con `usuario_ids: [u1, u2, u3]`, `materia_id: <mid>`, `carrera_id: <cid>`, `cohorte_id: <coid>`, `rol: "PROFESOR"`, `fecha_inicio: "2026-03-01"`, `fecha_fin: "2026-07-31"`
- **THEN** el sistema SHALL crear 3 asignaciones, una por cada usuario, y retornar `201 Created` con los registros creados

#### Scenario: Asignación masiva con usuario inexistente falla con rollback

- **WHEN** un COORDINADOR envía POST a `/api/equipos/asignacion-masiva` con `usuario_ids` que incluye un UUID inexistente
- **THEN** el sistema SHALL retornar `400 Bad Request` y NO crear ninguna asignación (rollback total)

#### Scenario: Asignación masiva con responsable_id opcional

- **WHEN** un ADMIN envía POST a `/api/equipos/asignacion-masiva` con `responsable_id` incluido
- **THEN** cada asignación creada SHALL tener ese `responsable_id`

#### Scenario: Asignación masiva sin permisos recibe 403

- **WHEN** un usuario sin `equipos:asignar` envía POST a `/api/equipos/asignacion-masiva`
- **THEN** el sistema SHALL retornar `403 Forbidden`

### Requirement: Clonar equipo docente entre cohortes (F4.5)

El sistema SHALL exponer un endpoint `POST /api/equipos/clonar` que reciba un origen (`materia_id`, `carrera_id`, `cohorte_origen_id`) y un destino (`cohorte_destino_id`, `fecha_inicio`, `fecha_fin`), y duplique todas las asignaciones vigentes (no soft-deleted) del origen al destino. Cada copia SHALL tener el nuevo `cohorte_id` y las fechas del destino. Guard: `equipos:asignar`.

#### Scenario: Clonado exitoso de equipo completo

- **WHEN** un COORDINADOR envía POST a `/api/equipos/clonar` con `materia_id: <mid>`, `carrera_id: <cid>`, `cohorte_origen_id: <coid-viejo>`, `cohorte_destino_id: <coid-nuevo>`, `fecha_inicio: "2026-08-01"`, `fecha_fin: "2026-12-31"`
- **THEN** el sistema SHALL crear N asignaciones (una por cada asignación vigente del origen) con `cohorte_id = <coid-nuevo>`, `fecha_inicio = "2026-08-01"`, `fecha_fin = "2026-12-31"`, y el resto de campos iguales al origen

#### Scenario: Clonado de equipo sin asignaciones origen

- **WHEN** un ADMIN envía POST a `/api/equipos/clonar` con un origen que no tiene asignaciones vigentes
- **THEN** el sistema SHALL retornar `200 OK` con `{ "creadas": 0 }` (operación exitosa pero sin efecto)

#### Scenario: Clonado con cohorte destino inexistente

- **WHEN** un COORDINADOR envía POST a `/api/equipos/clonar` con `cohorte_destino_id` que no existe
- **THEN** el sistema SHALL retornar `400 Bad Request`

#### Scenario: Clonado respeta multi-tenant

- **WHEN** un COORDINADOR del tenant A clona un equipo
- **THEN** solo SHALL clonar asignaciones del tenant A, incluso si el origen existe en otro tenant

### Requirement: Modificar vigencia general del equipo (F4.6)

El sistema SHALL exponer un endpoint `PATCH /api/equipos/vigencia` que reciba el scope del equipo (`materia_id`, `carrera_id`, `cohorte_id`) y las nuevas fechas (`fecha_inicio`, `fecha_fin`), y actualice todas las asignaciones del equipo que coincidan con el scope en una sola operación. Guard: `equipos:asignar`.

#### Scenario: Actualización de vigencia de todo un equipo

- **WHEN** un COORDINADOR envía PATCH a `/api/equipos/vigencia` con `materia_id: <mid>`, `carrera_id: <cid>`, `cohorte_id: <coid>`, `fecha_inicio: "2026-08-15"`, `fecha_fin: "2026-12-20"`
- **THEN** el sistema SHALL actualizar `fecha_inicio` y `fecha_fin` en todas las asignaciones que coinciden con el scope, y retornar la cantidad de registros afectados

#### Scenario: Actualización de vigencia sin equipo existente

- **WHEN** un ADMIN envía PATCH a `/api/equipos/vigencia` con un scope que no tiene asignaciones
- **THEN** el sistema SHALL retornar `200 OK` con `{ "afectadas": 0 }`

#### Scenario: Actualización de vigencia requiere equipos:asignar

- **WHEN** un usuario sin `equipos:asignar` envía PATCH a `/api/equipos/vigencia`
- **THEN** el sistema SHALL retornar `403 Forbidden`

### Requirement: Exportar equipo docente (F4.7)

El sistema SHALL exponer un endpoint `GET /api/equipos/exportar` que reciba filtros (`materia_id`, `carrera_id`, `cohorte_id`) y retorne un archivo CSV descargable con detalle de todas las asignaciones del equipo. Columnas del CSV: docente (nombre/apellido), rol, materia, carrera, cohorte, comisiones, vigencia desde, vigencia hasta, estado. Guard: `equipos:ver`.

#### Scenario: Exportación exitosa de equipo docente

- **WHEN** un COORDINADOR envía GET a `/api/equipos/exportar?materia_id=<mid>&carrera_id=<cid>&cohorte_id=<coid>`
- **THEN** el sistema SHALL retornar un CSV con `Content-Type: text/csv`, `Content-Disposition: attachment; filename="equipo-<mid>.csv"`, con una fila de header y una fila por cada asignación

#### Scenario: Exportación sin resultados

- **WHEN** un ADMIN envía GET a `/api/equipos/exportar` con filtros que no producen resultados
- **THEN** el sistema SHALL retornar un CSV con solo la fila de header (sin filas de datos)

#### Scenario: Exportación como streaming response

- **WHEN** un COORDINADOR exporta un equipo con 500+ asignaciones
- **THEN** el sistema SHALL retornar la respuesta como `StreamingResponse` (sin timeout ni uso excesivo de memoria)

#### Scenario: Exportación requiere equipos:ver

- **WHEN** un usuario sin `equipos:ver` envía GET a `/api/equipos/exportar`
- **THEN** el sistema SHALL retornar `403 Forbidden`
