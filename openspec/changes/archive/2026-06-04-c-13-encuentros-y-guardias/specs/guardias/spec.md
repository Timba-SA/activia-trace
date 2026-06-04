## ADDED Requirements

### Requirement: Registro de guardias por tutor

El sistema SHALL permitir a usuarios con permiso `guardias:registrar` crear y listar sus propias guardias. Cada guardia se asocia a una asignación (quién cubre), materia, carrera y cohorte.

#### Scenario: Tutor registra guardia exitosamente

- **WHEN** un usuario con permiso `guardias:registrar` envía POST con `asignacion_id`, `materia_id`, `carrera_id`, `cohorte_id`, `dia`, `horario`, `estado=Pendiente` y `comentarios` opcionales
- **THEN** el sistema SHALL crear la guardia con `creada_at` = timestamp actual y estado `Pendiente`

#### Scenario: Tutor lista sus propias guardias

- **WHEN** un usuario con permiso `guardias:registrar` envía GET a `/guardias` sin filtros
- **THEN** el sistema SHALL retornar solo las guardias donde `asignacion.usuario_id == current_user.id`, paginadas

### Requirement: Consulta global y exportación de guardias

El sistema SHALL permitir a usuarios con permiso `guardias:ver` consultar todas las guardias del tenant con filtros y exportarlas a CSV.

#### Scenario: Consulta global con filtros

- **WHEN** un usuario con permiso `guardias:ver` envía GET a `/guardias/admin` con filtros opcionales (`materia_id`, `carrera_id`, `cohorte_id`, `asignacion_id`, `estado`, `fecha_desde`, `fecha_hasta`)
- **THEN** el sistema SHALL retornar todas las guardias del tenant que coinciden con los filtros, paginadas

#### Scenario: Exportación CSV de guardias

- **WHEN** un usuario con permiso `guardias:ver` envía GET a `/guardias/exportar` con los mismos filtros opcionales
- **THEN** el sistema SHALL retornar un archivo CSV (`text/csv`) con las guardias filtradas, incluyendo columnas: tutor, materia, carrera, cohorte, día, horario, estado, comentarios, creada_at

### Requirement: Actualización de estado de guardia

El sistema SHALL permitir actualizar el estado de una guardia a `Realizada` o `Cancelada`.

#### Scenario: Marcar guardia como realizada

- **WHEN** un usuario con permiso `guardias:registrar` envía PATCH a `/guardias/{id}` con `estado=Realizada`
- **THEN** el sistema SHALL actualizar el estado de la guardia

#### Scenario: No se puede modificar una guardia realizada o cancelada

- **WHEN** un usuario envía PATCH a `/guardias/{id}` y la guardia tiene estado `Realizada` o `Cancelada`
- **THEN** el sistema SHALL retornar `400 Bad Request` porque las guardias no se modifican después de finalizadas
