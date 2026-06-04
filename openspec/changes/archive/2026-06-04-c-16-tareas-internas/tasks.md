## 1. Modelos y migración

- [x] 1.1 Crear modelo `Tarea` con tenant_id, estado (enum: Pendiente|En progreso|Resuelta|Cancelada), asignado_a (UUID FK Usuario), asignado_por (UUID FK Usuario), materia_id (UUID nullable FK Materia), contexto_id (UUID nullable), descripcion (Text), soft delete fields
- [x] 1.2 Crear modelo `ComentarioTarea` con tenant_id, tarea_id (UUID FK Tarea), autor_id (UUID FK Usuario), texto (Text), creado_at (datetime), soft delete fields
- [x] 1.3 Generar migration 014 con tablas `tarea` y `comentario_tarea` + índices compuestos por tenant + FK indexes

## 2. Schemas Pydantic

- [x] 2.1 Crear enum `EstadoTarea` (pendiente, en_progreso, resuelta, cancelada)
- [x] 2.2 Crear `TareaCreate`, `TareaUpdate`, `TareaResponse`, `TareaListResponse` con `extra='forbid'` y `from_attributes=True`
- [x] 2.3 Crear `ComentarioTareaCreate`, `ComentarioTareaResponse`

## 3. Repositories

- [x] 3.1 Crear `TareaRepository` con CRUD, listado paginado para mis-tareas (filtrado por asignado_a), y listado admin con filtros (asignado_a, asignado_por, materia_id, estado, búsqueda en descripcion)
- [x] 3.2 Crear `ComentarioTareaRepository` con create y list por tarea_id

## 4. Services

- [x] 4.1 Crear `TareasService` con métodos: crear_tarea, obtener_tarea, actualizar_tarea (estado+reasignar)
- [x] 4.2 Implementar `listar_mis_tareas(usuario_id)` que retorna tareas donde asignado_a = usuario_id, ordenado por created_at DESC
- [x] 4.3 Implementar `listar_tareas_admin(filtros)` con filtros combinados (asignado_a, asignado_por, materia_id, estado, q) scoped al tenant
- [x] 4.4 Implementar `cambiar_estado(tarea_id, nuevo_estado, usuario)` con validación de transiciones FL-05 (mapeo explícito de transiciones válidas + control de roles para Cancelar y devolver)
- [x] 4.5 Implementar `agregar_comentario(tarea_id, autor_id, texto)` y `listar_comentarios(tarea_id)`

## 5. Endpoints (Routers)

- [x] 5.1 Crear `tareas.py` router con POST /tareas, GET /tareas/{id}, PATCH /tareas/{id} — protegidos con `require_permission("tareas:gestionar")`
- [x] 5.2 Implementar GET /tareas — mis tareas (asignado_a = usuario actual), protegido con `require_permission("tareas:gestionar")`
- [x] 5.3 Implementar GET /tareas/admin — vista global con filtros, protegido con rol adicional COORDINADOR/ADMIN
- [x] 5.4 Implementar POST /tareas/{id}/comentarios y GET /tareas/{id}/comentarios como sub-recursos
- [x] 5.5 Registrar `tareas.router` en `api/v1/main.py` o router principal

## 6. Permisos RBAC

- [x] 6.1 Agregar permiso `tareas:gestionar` al seed de permisos en migration 014
- [x] 6.2 Asignar `tareas:gestionar` a PROFESOR, COORDINADOR y ADMIN en migration 014
- [x] 6.3 Agregar decoradores `require_permission` en endpoints de gestión

## 7. Tests

- [x] 7.1 Tests unitarios para servicios: creación de tarea, listado mis-tareas, listado admin con filtros, transiciones de estado válidas e inválidas, cancelación por COORDINADOR, agregar comentario
- [x] 7.2 Tests de integración para endpoints: CRUD tareas, mis-tareas, admin list, comentarios
- [x] 7.3 Tests de permisos: PROFESOR puede gestionar tareas, ALUMNO no puede, COORDINADOR puede cancelar y devolver
- [x] 7.4 Tests de edge cases: transición inválida retorna 409, reasignación cambia asignado_a, contexto_id nullable, soft delete excluye de listados
