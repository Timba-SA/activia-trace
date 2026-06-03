## 1. Contratos y base analítica

- [x] 1.1 Definir DTOs de filtros/respuestas para `/api/analisis/*` con validaciones (`extra='forbid'`, rango de fechas, paginación).
- [x] 1.2 Crear interfaces de repositorio de análisis (atrasados, ranking, agregados rápidos, notas agrupadas, monitores, exportables).
- [x] 1.3 Implementar/ajustar consultas tenant-scoped para datasets de calificaciones y finalización de actividades.

## 2. Reglas de negocio en services

- [x] 2.1 Implementar cálculo de alumnos atrasados (faltantes o nota bajo umbral) según RN-06.
- [x] 2.2 Implementar ranking de aprobadas filtrando solo alumnos con `>= 1` aprobada (RN-09).
- [x] 2.3 Implementar reporte rápido por materia con métricas agregadas y estado sin datos.
- [x] 2.4 Implementar notas finales agrupadas con la regla de agregación definida para C-11.

## 3. Monitores y filtros por rol

- [x] 3.1 Implementar resolución de `AccessScope` por sesión para tutor/profesor (asignaciones activas).
- [x] 3.2 Implementar monitor coordinación/admin con filtros extendidos y rango de fechas obligatorio/validado.
- [x] 3.3 Agregar ordenamiento determinista y paginación en ambos monitores.

## 4. Export TPs sin corregir

- [x] 4.1 Implementar correlación finalización vs calificación para detectar potenciales entregas sin corregir (RN-07/RN-08).
- [x] 4.2 Exponer endpoint de export CSV con filtros aplicados y headers estables.
- [x] 4.3 Garantizar que export vacío devuelva CSV válido con encabezados.

## 5. API, seguridad y auditoría

- [x] 5.1 Implementar routers `/api/analisis/*` con `require_permission("atrasados:ver")`.
- [x] 5.2 Asegurar identidad/scope exclusivamente desde sesión (sin aceptar identidad desde request).
- [-] 5.3 Registrar eventos de auditoría para consultas/export de análisis según convención del módulo.
  > _Bloqueado: C-05 (audit-log) no implementado — no existe infraestructura de auditoría aún._

## 6. Pruebas (Strict TDD)

- [x] 6.1 Crear tests de servicio para definición de atrasado (faltante + bajo umbral + no atrasado).
- [x] 6.2 Crear tests de ranking (incluye caso excluido por 0 aprobadas y orden descendente).
- [x] 6.3 Crear tests de notas finales agrupadas (con y sin datos por grupo).
- [x] 6.4 Crear tests de monitores por rol/filtros/rango de fechas y rechazo de rango inválido.
- [x] 6.5 Crear tests de export de TPs sin corregir (con filas y sin filas) y aislamiento por tenant.
