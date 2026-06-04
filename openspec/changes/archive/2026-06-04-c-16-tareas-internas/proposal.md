## Why

Coordinadores y docentes necesitan un sistema de tareas internas para gestionar trabajo administrativo y académico con trazabilidad: asignación, seguimiento de estado, comentarios y cierre. Actualmente no existe un mecanismo formal dentro de la plataforma; las tareas se manejan por canales externos sin trazabilidad ni auditoría.

## What Changes

- Nuevo modelo `Tarea` con estado (Pendiente|En progreso|Resuelta|Cancelada), asignado_a (FK Usuario), asignado_por (FK Usuario), materia_id nullable, contexto_id nullable, descripcion y timestamps
- Nuevo modelo `ComentarioTarea` con tarea_id (FK), autor_id (FK Usuario), texto y timestamps
- Endpoint `GET /api/tareas` — mis tareas asignadas al usuario autenticado
- Endpoint `GET /api/tareas/admin` — vista global con filtros (docente, asignador, materia, estado, búsqueda) para COORDINADOR/ADMIN
- Endpoint `POST /api/tareas` — crear tarea asignada a un docente
- Endpoint `GET /api/tareas/{id}` — obtener detalle
- Endpoint `PATCH /api/tareas/{id}` — cambiar estado y/o reasignar
- Endpoint `POST /api/tareas/{id}/comentarios` — agregar comentario
- Endpoint `GET /api/tareas/{id}/comentarios` — listar comentarios
- Flujo de estados FL-05: Pendiente → En progreso → Resuelta (docente); Cancelar (COORDINADOR/ADMIN)
- Nuevo permiso RBAC: `tareas:gestionar` (PROFESOR, COORDINADOR, ADMIN)
- Delta en spec `rbac` para el nuevo permiso
- Migration 014 con tablas `tarea` y `comentario_tarea`

## Capabilities

### New Capabilities
- `tareas-internas`: Workflow de tareas internas — asignación, seguimiento de estado, comentarios, vista personal y global con filtros

### Modified Capabilities
- `rbac`: Nuevo permiso `tareas:gestionar` asignado a PROFESOR, COORDINADOR y ADMIN

## Impact

- **Backend**: nuevos models, schemas, repository, service, router en `app/`
- **Base de datos**: migration 014 con 2 tablas nuevas (tarea, comentario_tarea) + índices
- **RBAC**: seed del permiso `tareas:gestionar` + delta spec
- **Dependencias**: C-07 (usuarios-y-asignaciones) completado — necesario para FK a Usuario
