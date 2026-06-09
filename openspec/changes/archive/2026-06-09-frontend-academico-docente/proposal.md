## Why

El backend académico (C-10 calificaciones, C-11 atrasados, C-12 comunicaciones) ya está completo. Los usuarios actuales (PROFESOR, TUTOR, COORDINADOR) no tienen interfaz para consumir esos endpoints — operan a ciegas. C-21 dejó el shell (layout, auth, router) listo. Este change construye la experiencia de usuario del flujo central del sistema (FL-02 y FL-04): importar calificaciones, detectar atrasados y comunicarse con alumnos.

## What Changes

- **Gestión de comisión**: selector de materia + cohorte, dashboard con métricas clave
- **Importación de calificaciones**: upload de archivo, preview de actividades detectadas, selección de actividades a incluir
- **Configuración de umbral**: slider/input de porcentaje de aprobación por materia, con persistencia
- **Vista de alumnos atrasados**: tabla con filtros, indicador de riesgo por alumno
- **Ranking y reportes rápidos**: ranking de actividades aprobadas, reportes consolidados por materia
- **Notas finales agrupadas**: cálculo y visualización de nota final por alumno
- **Entregas sin corregir**: detección vía reporte de finalización, exportación a CSV
- **Comunicación con atrasados**: preview de mensaje, envío masivo, tracking de estado en tiempo real (Pendiente → Enviando → OK/Fallido)
- **Monitores de seguimiento**: vista filtrable para TUTOR/PROFESOR del estado de actividades de alumnos asignados

## Capabilities

### New Capabilities

- `comision-gestion`: selector de materia × cohorte, dashboard con métricas y acceso a todas las secciones
- `calificaciones-importar`: upload de archivo LMS, preview de actividades detectadas, selección de actividades
- `umbral-configurar`: configuración del porcentaje de aprobación por materia con persistencia
- `atrasados-vista`: tabla de alumnos con actividades faltantes o低于 umbral, filtros por alumno/actividad
- `ranking-reportes`: ranking de actividades aprobadas, reportes rápidos con métricas clave
- `notas-finales`: agrupación de actividades y cálculo de nota final por alumno
- `entregas-sin-corregir`: detección de entregas pendientes de corrección, exportación CSV
- `comunicacion-envio`: preview de mensaje personalizado, envío masivo a atrasados, tracking de estado en tiempo real, aprobación
- `monitores-seguimiento`: vista filtrable del estado de actividades de alumnos asignados (TUTOR/PROFESOR)

### Modified Capabilities

- *(ninguna — primer change de frontend feature)*

## Impact

- Frontend: ~15 nuevas páginas/rutas, ~8 hooks TanStack Query, ~4 servicios API
- Consume endpoints de C-10 (calificaciones), C-11 (atrasados), C-12 (comunicaciones)
- Reusa Layout, ProtectedRoute, Axios client de C-21
- Sin cambios en backend
