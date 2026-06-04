## 1. Modelos y migración

- [x] 1.1 Crear modelo `Evaluacion` con tenant_id, materia_id, cohorte_id, tipo (enum: Parcial|TP|Coloquio|Recuperatorio), instancia (str), soft delete fields
- [x] 1.2 Crear modelo `TurnoDisponible` con tenant_id, evaluacion_id (FK), fecha (date), hora (time), cupo_total, cupos_restantes (default = cupo_total), soft delete fields
- [x] 1.3 Crear modelo `ReservaEvaluacion` con tenant_id, evaluacion_id, alumno_id, turno_id, fecha_hora (datetime), estado (enum: Activa|Cancelada), soft delete fields
- [x] 1.4 Crear modelo `ResultadoEvaluacion` con tenant_id, evaluacion_id, alumno_id, nota_final (text), soft delete fields
- [x] 1.5 Crear modelo `ConvocatoriaAlumno` (join table evaluacion_id + alumno_id para padrón de convocados) con soft delete
- [x] 1.6 Generar migration 012 con las 5 tablas nuevas + índices (tenant_id compuestos, FK a evaluacion)

## 2. Schemas Pydantic

- [x] 2.1 Crear `EvaluacionCreate`, `EvaluacionUpdate`, `EvaluacionResponse`, `EvaluacionListResponse` con `extra='forbid'`
- [x] 2.2 Crear `TurnoDisponibleCreate` (fecha, hora, cupo_total), `TurnoDisponibleResponse`
- [x] 2.3 Crear `ReservaCreate` (turno_id), `ReservaResponse`, `ReservaCancelResponse`
- [x] 2.4 Crear `ResultadoCreate` (alumno_id, nota_final), `ResultadoBatchCreate` (lista), `ResultadoResponse`
- [x] 2.5 Crear `ConvocatoriaAlumnoImport` (lista de user_ids), `MetricasResponse`, `ConvocatoriaListadoResponse` (con indicadores agregados)
- [x] 2.6 Crear enum `TipoEvaluacion` (Parcial, TP, Coloquio, Recuperatorio) y `EstadoReserva` (Activa, Cancelada)

## 3. Repositories

- [x] 3.1 Crear `EvaluacionRepository` con CRUD + listado paginado con indicadores (convocados, reservas, notas)
- [x] 3.2 Crear `TurnoDisponibleRepository` con CRUD + decremento atómico de cupo (`UPDATE ... SET cupos_restantes = cupos_restantes - 1 WHERE cupos_restantes > 0`)
- [x] 3.3 Crear `ReservaEvaluacionRepository` con create, cancel (soft delete + reincremento de cupo), verificación de duplicados
- [x] 3.4 Crear `ResultadoEvaluacionRepository` con create individual, create batch, list por evaluacion
- [x] 3.5 Crear `ConvocatoriaAlumnoRepository` con import batch (upsert), validación de existencia

## 4. Services

- [x] 4.1 Crear `ColoquiosService` con métodos: crear_convocatoria (crea Evaluacion + TurnoDisponible), actualizar_convocatoria, cerrar_convocatoria, listar_convocatorias
- [x] 4.2 Implementar `importar_padron` que recibe lista de user_ids, valida rol ALUMNO, upsert en ConvocatoriaAlumno
- [x] 4.3 Implementar `reservar_turno` con verificación de duplicado + decremento atómico de cupo, `cancelar_reserva` con reincremento
- [x] 4.4 Implementar `registrar_resultado` individual y batch con validación de padrón
- [x] 4.5 Implementar `obtener_metricas` con agregaciones (total_alumnos, instancias_activas, reservas_activas, notas_registradas)

## 5. Endpoints (Routers)

- [x] 5.1 Crear `evaluaciones.py` router: POST/GET/PATCH /convocatorias, GET /convocatorias/{id}, POST /convocatorias/{id}/importar-alumnos, POST /convocatorias/{id}/cerrar
- [x] 5.2 Crear `reservas.py` router: POST /reservas, PATCH /reservas/{id}/cancelar
- [x] 5.3 Crear `resultados.py` router: POST /resultados, POST /resultados/batch, GET /resultados?evaluacion_id=
- [x] 5.4 Crear `metricas.py` router: GET /metricas/coloquios

## 6. Permisos RBAC

- [x] 6.1 Agregar permisos `coloquios:gestionar`, `coloquios:ver`, `coloquios:reservar` al seed de permisos
- [x] 6.2 Asignar `coloquios:gestionar` a COORDINADOR y ADMIN
- [x] 6.3 Asignar `coloquios:ver` a COORDINADOR y ADMIN
- [x] 6.4 Asignar `coloquios:reservar` a ALUMNO
- [x] 6.5 Agregar decoradores `require_permission` en cada endpoint
- [x] 7.1 Registrar `evaluaciones.router` en `main.py`
- [x] 7.2 Registrar `reservas.router` en `main.py`
- [x] 7.3 Registrar `resultados.router` en `main.py`
- [x] 7.4 Registrar `metricas.router` en `main.py`

## 8. Tests

- [x] 8.1 Tests unitarios para servicios: creación de convocatoria, importación de padrón, reserva con decremento, cancelación con reincremento, registro de resultados
- [x] 8.2 Tests de integración para endpoints: CRUD convocatorias, reserva, resultados, métricas
- [x] 8.3 Tests de permisos: ALUMNO no puede gestionar, COORDINADOR no puede reservar
- [x] 8.4 Tests de edge cases: cupo agotado, reserva duplicada, padrón con usuarios inexistentes, batch con errores parciales
