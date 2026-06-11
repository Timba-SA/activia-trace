## Why

El backend de liquidaciones (C-18), facturas, grilla salarial, estructura académica (C-06), usuarios (C-07) y auditoría (C-19) ya está completo. Falta la interfaz de FINANZAS y ADMIN que consuma esos endpoints, completando el módulo de coordinación y administración del sistema.

## What Changes

- Nueva feature **FINANZAS**: vista de liquidación del período con segmentación (general / NEXO / factura), KPIs, cierre de liquidación, historial, exportación CSV, grilla salarial (ABM salarios base/plus/materia-grupo), gestión de facturas.
- Nueva feature **ADMIN**: estructura académica (ABM carreras, cohortes, materias), usuarios del tenant (listado, detalle, edición), panel de auditoría y métricas (acciones por día, por docente, por materia, comunicaciones, últimas acciones con filtros).
- Nuevas páginas lazy-loaded en Router.tsx + entradas en nav del Layout.
- Tests para cada página.

## Capabilities

### New Capabilities
- `liquidaciones`: Vista de liquidaciones del período, segmentación, cierre, historial, exportación CSV.
- `grilla-salarial`: ABM de salarios base, salarios plus y mapeo materia-grupo.
- `facturas`: Gestión de facturas (listado, crear, cambiar estado).
- `estructura-academica`: ABM de carreras, cohortes y materias.
- `usuarios-tenant`: Listado, detalle y edición de usuarios del tenant.
- `panel-auditoria`: Dashboard de métricas (acciones por día, por docente, por materia, comunicaciones) + log de últimas acciones con filtros.

### Modified Capabilities
- Ninguna (specs nuevas).

## Impact

- Frontend: nuevo módulo `frontend/src/features/finanzas/` y `frontend/src/features/admin/` con types, services, hooks, components, pages.
- Rutas nuevas: `/liquidaciones`, `/grilla-salarial`, `/facturas`, `/admin/carreras`, `/admin/cohortes`, `/admin/materias`, `/admin/usuarios`, `/admin/auditoria`.
- Layout: nuevas entradas en nav para Finanzas y Admin.
