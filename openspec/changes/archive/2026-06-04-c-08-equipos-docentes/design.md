## Context

El modelo `Asignacion` (C-07) tiene CRUD básico en `/api/admin/asignaciones` con permisos `usuarios:asignar`. Para Épica 4 se requiere una capa de gestión de equipos docentes con operaciones de alto nivel que van más allá del CRUD individual: vistas contextuales por usuario autenticado, asignación masiva transaccional, clonado entre cohortes, modificación de vigencia en bloque y exportación.

El stack es FastAPI async + SQLAlchemy 2.0 async + PostgreSQL. Patrón existente: Routers → Services → Repositories → Models.

## Goals / Non-Goals

**Goals:**
- Proveer endpoints de consulta con filtros para "mis equipos" (docente autenticado) y listado completo del tenant (COORDINADOR/ADMIN)
- Soportar creación en bloque de asignaciones en una sola transacción
- Implementar clonado de equipo origen → destino con fechas ajustadas
- Permitir actualización masiva de vigencia de todas las asignaciones de un equipo
- Exportar detalle del equipo en formato CSV
- Seed del permiso `equipos:asignar` para COORDINADOR y ADMIN

**Non-Goals:**
- No se modifica el modelo `Asignacion` existente (no hay migración de schema)
- No se toca el CRUD existente en `/api/admin/asignaciones`
- No se implementa frontend ni carga de archivos adjuntos
- No se implementa autocompletado server-side (F4.4 RN-30) — se hará en cambio posterior si aplica

## Decisions

### D1 — Router separado `/api/equipos` vs modificar `/api/admin/asignaciones`
- **Decisión**: Router nuevo `/api/equipos`
- **Razón**: El CRUD de asignaciones es de administración (`/api/admin/`). Los endpoints de equipos docentes son operaciones de gestión académica con semántica distinta. Separarlos evita mezclar responsabilidades y permite permisos diferenciados (`equipos:asignar` vs `usuarios:asignar`).
- **Alternativa**: Añadir endpoints al router existente. Descartado porque mezcla concern de admin con concern de gestión académica.

### D2 — Reutilizar AsignacionService vs crear EquipoService
- **Decisión**: Métodos nuevos en `AsignacionService` (sin clase separada)
- **Razón**: Todas las operaciones trabajan sobre el mismo modelo y repositorio. Una clase separada `EquipoService` duplicaría dependencias y no aportaría aislamiento real.
- **Alternativa**: Servicio separado. Descartado por sobreingeniería — las operaciones comparten repositorio y lógica de validación existente.

### D3 — Bulk create en una transacción vs individual con retry
- **Decisión**: Transacción única — si falla un registro, falla todo
- **Razón**: RN-30 describe una operación atómica de asignación masiva. El usuario espera que si algo falla, ninguna asignación se persista. Usamos `session.commit()` al final del batch. Compatible con el patrón existente (cada método de servicio hace un commit vía `BaseRepository.create`).

### D4 — Clonado: query source → adjust dates → bulk insert
- **Decisión**: READ de asignaciones vigentes del origen → copia cada una cambiando `cohorte_id` a destino y ajustando `fecha_inicio`/`fecha_fin` al nuevo período → bulk insert
- **Razón**: RN-12 especifica que se duplica el equipo "con las fechas del nuevo período". La estrategia más simple y transparente es copiar los registros modificando solo los campos que cambian. No se requiere lógica de mapeo compleja.

### D5 — Export: CSV con streaming response
- **Decisión**: `StreamingResponse` con `csv.writer` y UTF-8 BOM
- **Razón**: No hay dependencias externas — csv es parte de stdlib. Streaming evita cargar todo en memoria. El BOM asegura compatibilidad con Excel. No se justifica introducir openpyxl o similar.

### D6 — Nuevo permiso `equipos:asignar`
- **Decisión**: Se crea permiso `equipos:asignar` para COORDINADOR y ADMIN en el seed
- **Razón**: Los endpoints de gestión de equipos son distintos del CRUD de asignaciones. Separar permisos permite control granular. `equipos:ver` se usa para consultas (mis equipos), abierto a los roles docentes.

## Risks / Trade-offs

- **[Rendimiento en bulk create]** Asignación masiva de 100+ docentes podría timeoutear si la validación de FKs es secuencial. → Mitigación: validar usuarios en un solo query con `IN (...)` antes del loop de creación.
- **[Clonado con datos huérfanos]** Si la cohorte destino no tiene las mismas comisiones o materias, las referencias FK fallarán. → Mitigación: validar que `materia_id`, `carrera_id`, `cohorte_id` de destino existan antes de clonar.
- **[Permiso `equipos:ver` vs existentes]** Los docentes ya pueden ver sus datos vía JWT. El permiso `equipos:ver` se usa como guard en endpoints de consulta. → No conflictivo porque el CRUD de admin usa `usuarios:asignar`.
