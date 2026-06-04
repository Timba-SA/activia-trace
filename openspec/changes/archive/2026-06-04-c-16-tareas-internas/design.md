## Context

Módulo de tareas internas para active-trace. Permite a COORDINADOR, PROFESOR y ADMIN asignar tareas a docentes con seguimiento de estado y comentarios. Construye sobre C-07 (usuarios-y-asignaciones) para las FK a Usuario. El flujo de estados sigue la regla FL-05 del dominio: Pendiente → En progreso → Resuelta (docente), con Cancelar disponible para COORDINADOR/ADMIN en cualquier estado.

## Goals / Non-Goals

**Goals:**
- CRUD de tareas con permiso `tareas:gestionar` (PROFESOR, COORDINADOR, ADMIN)
- Vista personal de tareas asignadas al usuario autenticado
- Vista global con filtros para COORDINADOR/ADMIN
- Comentarios como sub-recurso de tarea con trazabilidad de autor
- Flujo de estados controlado por reglas de negocio (FL-05)
- Soft delete en ambas tablas
- Tenant isolation en todas las operaciones

**Non-Goals:**
- No incluye notificaciones al asignar una tarea (se integra con C-12 comunicaciones)
- No incluye frontend — solo API REST
- No incluye workflow engine ni BPMN — el estado es un enum con validación en service

## Decisions

### D1 — Enum-based estado (no workflow engine)
El estado de Tarea es un enum `EstadoTarea` (Pendiente, En progreso, Resuelta, Cancelada). La máquina de estados se valida en el service `TareasService.cambiar_estado()` con transiciones explícitas:
- Pendiente → En progreso (asignado)
- Pendiente → Cancelada (COORDINADOR/ADMIN)
- En progreso → Resuelta (asignado)
- En progreso → Cancelada (COORDINADOR/ADMIN)
- Resuelta → Pendiente (solo COORDINADOR/ADMIN — devolución)
- Cualquier estado → Cancelada (solo COORDINADOR/ADMIN)

Esto es más simple que un workflow engine y suficiente para el dominio actual. Si en el futuro se necesitan transiciones más complejas, se puede migrar a un patrón state machine.

### D2 — Two-endpoint strategy: mis-tareas vs /admin
Se exponen dos endpoints de listado:
- `GET /api/tareas` — retorna tareas donde `asignado_a = usuario_actual`. Cualquier usuario con `tareas:gestionar` puede ver sus propias tareas.
- `GET /api/tareas/admin` — retorna todas las tareas del tenant con filtros (asignado_a, asignado_por, materia_id, estado, búsqueda en descripcion). Solo COORDINADOR/ADMIN.

Esto separa claramente el caso de uso personal del administrativo, simplifica la lógica de autorización y evita filtros confusos en un solo endpoint.

### D3 — Comentarios como sub-recurso anidado
Los comentarios se gestionan como sub-recurso de `/tareas/{id}/comentarios`. Cada comentario tiene autor_id (FK Usuario), texto y timestamp. Esto mantiene la jerarquía clara y permite paginación independiente. No hay edición ni soft delete de comentarios individuales — se consideran registro de auditoría inmutable.

### D4 — contexto_id como UUID polimórfico simple
El campo `contexto_id` en Tarea es un UUID nullable sin FK estricta. Permite asociar la tarea a cualquier entidad del dominio (entrega, encuentro, coloquio) sin crear tablas polimórficas ni FK condicionales. La interpretación del contexto es responsabilidad del frontend o de la capa de presentación. No hay validación de integridad referencial para este campo.

### D5 — Un solo router `tareas` con 6 endpoints
Se agrupa toda la funcionalidad en `tareas.py` router: CRUD de gestión, mis-tareas, admin-list, comentarios. Un solo service `TareasService` orquesta toda la lógica. Esto es apropiado para un módulo cohesivo.

## Risks / Trade-offs

- **contexto_id sin FK**: No hay integridad referencial a nivel BD. Si se referencia una entidad que no existe, la tarea queda huérfana. Mitigación: el campo es nullable y opcional; su uso se validará en la capa de aplicación si se requiere.
- **Transiciones de estado inválidas**: Si un docente intenta saltar de Pendiente a Resuelta sin pasar por En progreso, el service debe rechazarlo. Esto se valida con un mapa de transiciones explícito en el método `cambiar_estado()`.
- **Permiso `tareas:gestionar`**: Es un permiso compartido por PROFESOR, COORDINADOR y ADMIN. Las operaciones de administración (vista global, cancelar, devolver) se controlan por rol adicional dentro del service, no por permiso separado.
