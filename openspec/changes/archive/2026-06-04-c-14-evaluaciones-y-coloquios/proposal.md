## Why

La gestión de coloquios y evaluaciones orales se realiza actualmente fuera del sistema, sin trazabilidad ni control de cupos. Los coordinadores no pueden publicar convocatorias con días y horarios disponibles, los alumnos no pueden auto-reservar turnos, y los resultados quedan descentralizados. Este módulo centraliza todo el ciclo: convocatoria → reserva → resultado, con trazabilidad completa multi-tenant.

## What Changes

- Nuevo modelo `Evaluacion` (convocatoria de examen: parcial, TP, coloquio, recuperatorio)
- Nuevo modelo `TurnoDisponible` (días y cupos por fecha/hora dentro de una convocatoria)
- Nuevo modelo `ReservaEvaluacion` (reserva de turno por alumno con decremento atómico de cupo)
- Nuevo modelo `ResultadoEvaluacion` (nota final del alumno en la evaluación)
- Endpoints CRUD para convocatorias (COORDINADOR, ADMIN)
- Endpoint de importación de padrón de alumnos habilitados por convocatoria
- Endpoint de reserva/cancelación de turno por ALUMNO
- Endpoint de registro consolidado de resultados (COORDINADOR/ADMIN)
- Panel de métricas: total alumnos, instancias activas, reservas activas, notas registradas
- 3 nuevos permisos RBAC: `coloquios:gestionar`, `coloquios:ver`, `coloquios:reservar`

## Capabilities

### New Capabilities
- `coloquios`: Gestión completa de coloquios — convocatorias con turnos, reservas, resultados y métricas

### Modified Capabilities
- `rbac`: Nuevos permisos `coloquios:gestionar`, `coloquios:ver`, `coloquios:reservar`

## Impact

- **Backend**: nuevos models, schemas, repositories, services, routers en `app/`
- **Base de datos**: migration 012 con 4 tablas nuevas (evaluacion, turno_disponible, reserva_evaluacion, resultado_evaluacion)
- **Permissions**: seed de nuevos permisos en RBAC
- **Dependencias**: C-07 (usuarios-y-asignaciones) ya completado — necesario para relaciones con Usuario y Materia
