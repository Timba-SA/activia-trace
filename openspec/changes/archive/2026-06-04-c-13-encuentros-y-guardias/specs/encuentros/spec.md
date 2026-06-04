## ADDED Requirements

### Requirement: CRUD de slots de encuentro

El sistema SHALL permitir a usuarios con permiso `encuentros:gestionar` crear, listar, ver y eliminar slots de encuentro (`SlotEncuentro`). Un slot es una plantilla de recurrencia semanal que define día de la semana, horario, materia, título y enlace de videoconferencia.

#### Scenario: Crear slot recurrente exitosamente

- **WHEN** un usuario con permiso `encuentros:gestionar` envía una solicitud POST con `materia_id`, `asignacion_id`, `titulo`, `hora`, `dia_semana`, `fecha_inicio`, `cant_semanas` (positivo) y `meet_url`
- **THEN** el sistema SHALL crear el slot y generar automáticamente `cant_semanas` instancias de encuentro con estado `Programado`, una por cada semana desde `fecha_inicio`

#### Scenario: Crear slot de fecha única exitosamente

- **WHEN** un usuario con permiso `encuentros:gestionar` envía una solicitud POST con `cant_semanas=0`, `fecha_unica` set, `dia_semana`, `hora`, `titulo` y `meet_url`
- **THEN** el sistema SHALL crear el slot y generar una única instancia de encuentro en la fecha indicada

#### Scenario: Validación mutuamente excluyente de modo

- **WHEN** un usuario envía POST con `cant_semanas=0` Y `fecha_unica=NULL`
- **THEN** el sistema SHALL retornar `422 Unprocessable Entity` indicando que debe especificar modo recurrente o fecha única

#### Scenario: Validación de límite de semanas

- **WHEN** un usuario envía POST con `cant_semanas > 52`
- **THEN** el sistema SHALL retornar `422 Unprocessable Entity` indicando que el máximo es 52 semanas

#### Scenario: Listar slots con filtros

- **WHEN** un usuario con permiso `encuentros:gestionar` envía GET con `materia_id` y `asignacion_id` opcionales
- **THEN** el sistema SHALL retornar la lista paginada de slots del tenant con su materia y asignación asociadas

#### Scenario: Eliminar slot (soft delete)

- **WHEN** un usuario con permiso `encuentros:gestionar` envía DELETE a un slot existente
- **THEN** el sistema SHALL marcar el slot como eliminado (soft delete) sin afectar las instancias ya creadas

### Requirement: CRUD de instancias de encuentro

El sistema SHALL permitir gestionar instancias concretas de encuentro (`InstanciaEncuentro`). Cada instancia tiene estado independiente del slot que la originó (RN-14).

#### Scenario: Crear instancia independiente (sin slot)

- **WHEN** un usuario con permiso `encuentros:gestionar` envía POST con `materia_id`, `fecha`, `hora`, `titulo`, `meet_url` y `slot_id=NULL`
- **THEN** el sistema SHALL crear una instancia de encuentro única con estado `Programado`

#### Scenario: Actualizar instancia (estado, meet_url, video_url, comentario)

- **WHEN** un usuario con permiso `encuentros:gestionar` envía PATCH a `/instancias/{id}` con `estado`, `meet_url`, `video_url` y/o `comentario`
- **THEN** el sistema SHALL actualizar solo los campos provistos de la instancia

#### Scenario: No se permite modificar slot_id ni materia_id en update

- **WHEN** un usuario envía PATCH a `/instancias/{id}` con `slot_id` o `materia_id` diferentes
- **THEN** el sistema SHALL ignorar esos campos (no están en el schema de update)

#### Scenario: Listar instancias por slot

- **WHEN** un usuario envía GET con `slot_id`
- **THEN** el sistema SHALL retornar todas las instancias asociadas a ese slot, ordenadas por fecha ascendente

#### Scenario: Vista transversal de instancias (admin)

- **WHEN** un usuario con permiso `encuentros:ver` envía GET con filtros opcionales (`materia_id`, `estado`, `fecha_desde`, `fecha_hasta`)
- **THEN** el sistema SHALL retornar todas las instancias del tenant sin filtrar por docente, paginadas

### Requirement: Exportación HTML para aula virtual

El sistema SHALL generar un fragmento HTML formateado con los encuentros programados de una materia, listo para publicar en el LMS.

#### Scenario: Generar HTML de encuentros

- **WHEN** un usuario con permiso `encuentros:gestionar` envía GET a `/encuentros/exportar-html?materia_id=UUID`
- **THEN** el sistema SHALL retornar un bloque HTML (`text/html`) con tabla de encuentros futuros de esa materia

#### Scenario: HTML incluye solo encuentros futuros y realizados con video

- **WHEN** el HTML se genera para una materia
- **THEN** SHALL incluir encuentros con estado `Programado` (futuros) y `Realizado` con `video_url` no nula
