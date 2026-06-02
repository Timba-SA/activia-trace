## Why

El flujo central del PROFESOR es importar calificaciones desde el LMS, analizar el estado de los alumnos y detectar atrasados. C-09 ya provee la ingesta del padrón; este change agrega el modelo de calificaciones y umbrales de aprobación que permitirán en C-11 computar atrasados, rankings y notas finales.

## What Changes

- Nuevo modelo `Calificacion` con soporte de notas numéricas y textuales, `aprobado` derivado (denormalizado), origen Importado/Manual
- Nuevo modelo `UmbralMateria` con umbral_pct configurable por materia y valores_aprobados textuales
- Endpoint `POST /api/v1/calificaciones/import/preview` — subir archivo, detectar columnas numéricas vs textuales, devolver vista previa
- Endpoint `POST /api/v1/calificaciones/import/confirm` — el usuario selecciona actividades, confirma, bulk create
- Endpoint `GET /api/v1/calificaciones` — listar calificaciones con filtros materia/cohorte
- Endpoint `GET /api/v1/umbrales` — obtener umbral por materia
- Endpoint `PUT /api/v1/umbrales/{id}` — actualizar umbral_pct y valores_aprobados
- Permisos nuevos: `calificaciones:configurar-umbral` agregado a PROFESOR, COORDINADOR, ADMIN
- Migración Alembic 007: tablas `calificacion` y `umbral_materia`

## Capabilities

### New Capabilities
- `calificaciones-import`: Importación de calificaciones desde archivo LMS con detección de columnas numéricas/textuales, vista previa y confirmación
- `umbrales-configuracion`: Configuración de umbral de aprobación por materia (porcentaje y valores textuales aprobatorios)
- `calificaciones-consulta`: Consulta de calificaciones por materia y cohorte

### Modified Capabilities
- (ninguna — primer módulo de calificaciones)

## Impact

- Backend: nuevos modelos, repositorios, servicio, router, schemas para Calificacion y UmbralMateria
- Base de datos: una migración con 2 tablas nuevas
- Permisos: seed de `calificaciones:configurar-umbral` en PROFESOR, COORDINADOR y ADMIN
- Dependencias: C-09 (padrón) completado — usamos EntradaPadron como FK
