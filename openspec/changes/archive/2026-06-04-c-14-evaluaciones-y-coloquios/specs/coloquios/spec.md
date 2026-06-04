## ADDED Requirements

### Requirement: Gestión de convocatorias

El sistema SHALL permitir a usuarios con permiso `coloquios:gestionar` crear, editar y cerrar convocatorias de evaluación (Evaluacion) especificando materia, instancia, tipo, y un conjunto de turnos disponibles con fecha, hora y cupo.

#### Scenario: Creación exitosa de convocatoria

- **WHEN** un COORDINADOR envía datos de convocatoria con materia_id, instancia, tipo, y 3 turnos con fecha/hora/cupo
- **THEN** el sistema crea la Evaluacion y los TurnoDisponible asociados, y retorna la convocatoria con sus turnos

#### Scenario: Error al crear convocatoria sin turnos

- **WHEN** un COORDINADOR envía una convocatoria sin turnos disponibles
- **THEN** el sistema retorna error 422 indicando que se requiere al menos un turno

### Requirement: Importación de padrón de alumnos

El sistema SHALL permitir a usuarios con permiso `coloquios:gestionar` importar una lista de alumnos habilitados para una convocatoria. SHALL validar que cada usuario exista y tenga rol ALUMNO. SHALL ignorar duplicados sin error.

#### Scenario: Importación exitosa con 3 alumnos

- **WHEN** un COORDINADOR envía una lista de 3 user_ids válidos con rol ALUMNO para una Evaluacion
- **THEN** el sistema asocia los 3 alumnos a la convocatoria y retorna count = 3

#### Scenario: Importación con alumno inexistente

- **WHEN** un COORDINADOR envía una lista que incluye un user_id que no existe
- **THEN** el sistema retorna error 404 indicando qué usuario no fue encontrado

### Requirement: Reserva de turno por ALUMNO

El sistema SHALL permitir a usuarios con permiso `coloquios:reservar` (ALUMNO) reservar un turno disponible en una convocatoria. SHALL decrementar atómicamente `cupos_restantes` del TurnoDisponible. SHALL rechazar la reserva si el cupo está agotado o el alumno ya tiene una reserva activa en la misma Evaluacion.

#### Scenario: Reserva exitosa con cupo disponible

- **WHEN** un ALUMNO reserva un TurnoDisponible con cupos_restantes = 5
- **THEN** el sistema crea una ReservaEvaluacion activa y decrementa cupos_restantes a 4

#### Scenario: Rechazo por cupo agotado

- **WHEN** un ALUMNO reserva un TurnoDisponible con cupos_restantes = 0
- **THEN** el sistema retorna error 409 indicando que no hay cupos disponibles

#### Scenario: Rechazo por reserva duplicada

- **WHEN** un ALUMNO intenta reservar un segundo turno en la misma Evaluacion teniendo ya una reserva activa
- **THEN** el sistema retorna error 409 indicando que ya tiene una reserva activa en esta convocatoria

#### Scenario: Cancelación de reserva y reincremento de cupo

- **WHEN** un ALUMNO cancela su reserva activa
- **THEN** el sistema cambia el estado a Cancelada y reincrementa cupos_restantes del TurnoDisponible en 1

### Requirement: Registro de resultados

El sistema SHALL permitir a usuarios con permiso `coloquios:gestionar` registrar el resultado (nota_final) de un alumno en una Evaluacion. SHALL permitir registro individual y masivo. SHALL rechazar si el alumno no está en el padrón de la convocatoria.

#### Scenario: Registro individual exitoso

- **WHEN** un COORDINADOR registra nota_final = "8.50" para un alumno en una Evaluacion
- **THEN** el sistema crea un ResultadoEvaluacion con esa nota

#### Scenario: Registro masivo exitoso

- **WHEN** un COORDINADOR envía una lista de 5 {alumno_id, nota_final} para una Evaluacion
- **THEN** el sistema crea 5 ResultadoEvaluacion y retorna count = 5

#### Scenario: Rechazo por alumno no convocado

- **WHEN** un COORDINADOR registra nota para un alumno que no está en el padrón de la Evaluacion
- **THEN** el sistema retorna error 409 indicando que el alumno no está habilitado

### Requirement: Panel de métricas

El sistema SHALL exponer un endpoint de métricas accesible con permiso `coloquios:ver` que retorne: total de alumnos cargados en padrón, instancias activas, reservas activas y notas registradas.

#### Scenario: Métricas retornan datos consolidados

- **WHEN** un COORDINADOR consulta el panel de métricas
- **THEN** el sistema retorna un objeto con total_alumnos, instancias_activas, reservas_activas, notas_registradas

### Requirement: Listado de convocatorias con indicadores

El sistema SHALL exponer un listado paginado de convocatorias accesible con permiso `coloquios:ver` que muestre por cada una: materia, instancia, total de turnos, total de convocados, reservas activas, cupos libres, notas registradas.

#### Scenario: Listado retorna indicadores

- **WHEN** un COORDINADOR consulta el listado de convocatorias
- **THEN** cada convocatoria incluye materia_nombre, instancia, total_turnos, total_convocados, reservas_activas, cupos_libres, notas_registradas
