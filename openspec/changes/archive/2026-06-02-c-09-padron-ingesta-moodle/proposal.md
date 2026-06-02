## Why

El sistema necesita un módulo de **Padrón** que gestione la carga versionada de listados de alumnos por materia+cohorte, con soporte para importación manual (xlsx/csv) y sincronización automática con Moodle Web Services. Sin esto, no hay base para calificaciones, comunicación con alumnos ni análisis académico.

## What Changes

- **Nuevos modelos**: `VersionPadron` y `EntradaPadron` con tenant isolation y soft delete
- **Nuevo módulo de importación**: subida de archivo → preview → confirmación → creación de versión
- **Nuevo cliente Moodle WS** en `integrations/moodle_ws.py` con sync de usuarios/actividades
- **Nuevas rutas API** bajo `/api/v1/padron` protegidas con permiso `padron:cargar`
- **Migración Alembic 006** con las nuevas tablas
- **Seed update**: agregar permiso `padron:cargar` a ADMIN y COORDINADOR
- Solo una versión activa por (materia_id, cohorte_id); activar una nueva desactiva la anterior

## Capabilities

### New Capabilities
- `padron`: Gestión versionada de padrón de alumnos con importación xlsx/csv y preview

### Modified Capabilities
<!-- None -->

## Impact

- `backend/app/models/version_padron.py`, `backend/app/models/entrada_padron.py`
- `backend/app/schemas/padron.py`
- `backend/app/repositories/padron_repository.py`
- `backend/app/services/padron_service.py`
- `backend/app/api/v1/routers/padron.py`
- `backend/app/integrations/moodle_ws.py`
- `backend/alembic/versions/006_padron.py`
- `backend/scripts/seed_permissions.py` (update)
- `backend/app/main.py` (register router)
