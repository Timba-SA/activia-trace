## Why

COORDINADOR y ADMIN necesitan un registro centralizado de los programas oficiales de cada materia (documentos) y la calendarización de fechas de evaluaciones (parciales, TP, coloquios, recuperatorios) por materia × cohorte. Actualmente ambos se manejan fuera de la plataforma sin trazabilidad. Además, se requiere generar contenido HTML ready para publicar en el LMS a partir del programa activo.

## What Changes

- Nuevo modelo `ProgramaMateria` con materia_id, carrera_id, cohorte_id nullable, referencia_archivo, contenido_html nullable, version, activo, aprobado_en
- Nuevo modelo `FechaAcademica` con materia_id, cohorte_id, tipo (Parcial|TP|Coloquio|Recuperatorio), numero nullable, fecha, hora nullable, aula nullable, observaciones nullable
- Endpoint `GET /api/programas` — listar programas con filtros materia_id, carrera_id, cohorte_id, activo
- Endpoint `POST /api/programas` — crear programa (COORDINADOR, ADMIN)
- Endpoint `GET /api/programas/{id}` — obtener detalle
- Endpoint `PATCH /api/programas/{id}` — actualizar programa
- Endpoint `DELETE /api/programas/{id}` — soft delete (desactivar)
- Endpoint `POST /api/programas/{id}/generar-contenido` — generar fragmento HTML ready para LMS
- Endpoint `GET /api/fechas-academicas` — listar fechas con filtros materia_id, cohorte_id, tipo
- Endpoint `POST /api/fechas-academicas` — crear fecha (COORDINADOR, ADMIN)
- Endpoint `GET /api/fechas-academicas/{id}` — obtener detalle
- Endpoint `PATCH /api/fechas-academicas/{id}` — actualizar fecha
- Endpoint `DELETE /api/fechas-academicas/{id}` — eliminar (soft delete)
- Nuevos permisos RBAC: `programas:gestionar` (COORDINADOR, ADMIN), `programas:ver`
- Migration 015 con tablas `programa_materia` y `fecha_academica`

## Capabilities

### New Capabilities
- `programas-materia`: Gestión de programas oficiales de materia — alta, actualización, versionado, activación/desactivación, generación de contenido HTML para LMS
- `fechas-academicas`: Calendarización de instancias evaluativas (parciales, TP, coloquios, recuperatorios) por materia × cohorte

### Modified Capabilities
- `rbac`: Nuevos permisos `programas:gestionar` y `programas:ver` asignados a COORDINADOR y ADMIN

## Impact

- **Backend**: nuevos models (ProgramaMateria, FechaAcademica), schemas, repositories, services, router en `app/`
- **Base de datos**: migration 015 con 2 tablas nuevas (programa_materia, fecha_academica) + índices
- **RBAC**: seed de nuevos permisos + delta spec
- **Dependencias**: C-06 (estructura-academica) completado — necesario para FK a Materia, Carrera, Cohorte
