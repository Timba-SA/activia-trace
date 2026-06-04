## Context

Módulo de coloquios para active-trace. Permite a COORDINADOR/ADMIN crear convocatorias de evaluación oral con días y cupos, a ALUMNO reservar turnos, y a COORDINADOR/ADMIN registrar resultados. Multi-tenant row-level, soft delete en todas las entidades. Construye sobre C-07 (usuarios-y-asignaciones) para las relaciones con Usuario y Materia.

## Goals / Non-Goals

**Goals:**
- Crear/editar/cerrar convocatorias (Evaluacion) con días y cupos (TurnoDisponible)
- Importar padrón de alumnos habilitados por convocatoria
- Reserva y cancelación de turnos por ALUMNO con decremento atómico de cupos
- Registro consolidado de resultados (ResultadoEvaluacion)
- Panel de métricas: alumnos cargados, instancias activas, reservas activas, notas registradas
- 3 nuevos permisos RBAC: `coloquios:gestionar`, `coloquios:ver`, `coloquios:reservar`

**Non-Goals:**
- No incluye flujo de aprobación de reservas (la reserva es directa si hay cupo)
- No incluye notificaciones push/email (se integra con C-12 comunicaciones)
- No incluye recalificación ni historial de cambios de nota (solo resultado final)

## Decisions

### D1 — TurnoDisponible como modelo separado de Evaluacion
En lugar de usar `dias_disponibles` como un int genérico en Evaluacion (como sugiere la KB), se crea `TurnoDisponible` con fecha, hora, cupo_total y cupos_restantes. Esto permite granularidad por día, consistencia transaccional en el decremento y consultas eficientes de disponibilidad.

### D2 — Decremento atómico de cupos vía UPDATE con CHECK
La reserva decrementa `cupos_restantes` en una sola sentencia `UPDATE turno_disponible SET cupos_restantes = cupos_restantes - 1 WHERE cupos_restantes > 0 AND id = X`. Si `rowcount = 0`, se rechaza la reserva (cupo agotado). No hay race condition ni necesidad de locks explícitos.

### D3 — ReservaEvaluacion como modelo independiente
Se separa la reserva del resultado. La reserva es un acto del ALUMNO; el resultado lo registra COORDINADOR/ADMIN después de la evaluación. Esto refleja el flujo real.

### D4 — Endpoints organizados por recurso
Routers separados: `evaluaciones` (convocatorias + turnos), `reservas` (reserva/cancelación por ALUMNO), `resultados` (registro/consulta por COORDINADOR), `metricas` (panel). Un único service `coloquios` orquesta la lógica.

### D5 — Nota como texto (no numérico)
`ResultadoEvaluacion.nota_final` es texto para soportar tanto valores numéricos (8.50) como cualitativos (Aprobado/Regular/Insuficiente), según la configuración de cada institución.

## Risks / Trade-offs

- **Race condition en cupo final**: el UPDATE atómico elimina race conditions clásicas, pero en alta concurrencia el último cupo podría asignarse a dos requests simultáneos — mitigado por `cupos_restantes > 0` en el WHERE y verificación de rowcount
- **Padrón de alumnos**: la importación requiere que los usuarios existan con rol ALUMNO. Si no hay alumnos cargados, la convocatoria no puede publicarse. Mitigación: el endpoint valida existencia y retorna error claro.
- **Soft delete en reservas canceladas**: al cancelar una reserva, se hace soft delete (activa → cancelada) y se REINCREMENTA `cupos_restantes` del `TurnoDisponible` asociado
