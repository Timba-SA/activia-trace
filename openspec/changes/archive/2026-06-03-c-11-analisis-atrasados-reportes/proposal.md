## Why

El flujo central del PROFESOR ya importa calificaciones y configura umbrales (C-10), pero todavía no convierte esos datos en priorización accionable. Este change habilita análisis de atraso, ranking y reportes operativos para detectar riesgo académico temprano y preparar comunicación/seguimiento.

## What Changes

- Agregar endpoints `/api/analisis/*` con guard `atrasados:ver` para: atrasados, ranking, reportes rápidos y notas finales agrupadas.
- Incorporar exportación de TPs sin corregir (cruce entre finalización de actividades y calificaciones registradas).
- Implementar monitores de seguimiento con filtros por rol:
  - Tutor/Profesor: alcance sobre sus alumnos asignados.
  - Coordinación/Admin: vista global del tenant + filtro por rango de fechas.
- Estandarizar criterios de cálculo de atraso (faltante o nota bajo umbral), ranking (solo alumnos con ≥1 aprobada) y agregación de nota final.

## Capabilities

### New Capabilities
- `analisis-atrasados-reportes`: Cómputo de atrasados, ranking, reportes rápidos por materia y notas finales agrupadas.
- `entregas-sin-corregir-export`: Detección y exportación de entregas finalizadas sin calificación asociada.
- `monitores-seguimiento`: Monitores filtrables por rol (tutor/profesor vs coordinación/admin con rango de fechas).

### Modified Capabilities
- `calificaciones-consulta`: Extender consultas para soportar agregaciones necesarias del análisis (totales aprobadas/faltantes y datasets base para reportes).

## Impact

- Backend (dominio y aplicación): nuevos services de análisis, repositorios de agregación y validación de filtros por rol/tenant.
- API: nuevos endpoints `/api/analisis/*` y contrato de exportación.
- Seguridad: uso obligatorio de identidad de sesión + tenant scoping en todas las consultas analíticas.
- Datos: reutiliza `Calificacion`, `UmbralMateria`, `EntradaPadron` y dataset de finalización de actividades (sin cambio de esquema obligatorio en esta fase).
