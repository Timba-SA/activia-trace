## Why

Los coordinadores y administradores necesitan un canal oficial de comunicación institucional dentro del sistema para publicar avisos urgentes, advertencias o información general, segmentados por audiencia (rol, materia, cohorte) y con posibilidad de exigir acuse de recibo. Actualmente no existe un tablón de avisos centralizado; las comunicaciones importantes se pierden en la mensajería interna o se manejan fuera del sistema.

## What Changes

- Nuevo modelo `Aviso` con alcance (Global|PorMateria|PorCohorte|PorRol), segmentación por materia/cohorte/rol, severidad (Info|Advertencia|Crítico), ventana de vigencia, orden, activo/inactivo y requiere_ack
- Nuevo modelo `AcknowledgmentAviso` que registra confirmaciones de lectura por usuario
- Endpoints CRUD de avisos para COORDINADOR/ADMIN (permiso `avisos:publicar`)
- Endpoint `GET /api/avisos/mis-avisos` — avisos filtrados por audiencia del usuario actual
- Endpoint `POST /api/avisos/{id}/ack` — confirmar lectura (acuse de recibo)
- Endpoint `GET /api/avisos/{id}/stats` — contadores de vistas y confirmaciones derivados
- Nuevo permiso RBAC: `avisos:publicar` (COORDINADOR, ADMIN)
- Delta en spec `rbac` para el nuevo permiso
- Migration 013 con tablas `aviso` y `acknowledgment_aviso`

## Capabilities

### New Capabilities
- `avisos`: Tablón de avisos del sistema — publicación segmentada con alcance, severidad, vigencia, orden y acuse de recibo obligatorio

### Modified Capabilities
- `rbac`: Nuevo permiso `avisos:publicar` asignado a COORDINADOR y ADMIN

## Impact

- **Backend**: nuevos models, schemas, repository, service, router en `app/`
- **Base de datos**: migration 013 con 2 tablas nuevas (aviso, acknowledgment_aviso) + índices
- **RBAC**: seed del permiso `avisos:publicar` + delta spec
- **Dependencias**: C-06 (estructura-academica) completado — necesario para FK a Materia y Cohorte; C-07 (usuarios-y-asignaciones) completado — necesario para FK a Usuario
