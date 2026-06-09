## 1. Feature scaffolding y contexto compartido

- [x] 1.1 Crear `features/academico/` con estructura: `components/`, `hooks/`, `services/`, `types/`, `pages/`, `context/`
- [x] 1.2 Crear `AcademicoContext` con materiaId, cohorteId, periodo seleccionado
- [x] 1.3 Crear `AcademicoProvider` que envuelve las rutas y persiste selección en sessionStorage
- [x] 1.4 Crear `services/api.ts` con endpoints del feature (materias, cohortes, calificaciones, umbral, atrasados, ranking, notas, entregas, comunicaciones, monitoreo)

## 2. Comisión selector y dashboard

- [x] 2.1 Crear `ComisionSelector` con dropdown de materia y cohorte
- [x] 2.2 Crear `ComisionPage` (dashboard) con KPIs: total alumnos, atrasados, actividades
- [x] 2.3 Crear `DashboardMetrics` con cards de métricas (reutilizando patron de C-21)
- [x] 2.4 Integrar en Router bajo `/academico/:materiaId?/:cohorteId?` con ProtectedRoute `calificaciones:ver`

## 3. Importación de calificaciones

- [x] 3.1 Crear hook `useCalificaciones` con TanStack Query: GET calificaciones, POST importar, POST confirmar, DELETE vaciar
- [x] 3.2 Crear `ImportPreview` con tabla de actividades detectadas y checkboxes
- [x] 3.3 Crear `CalificacionesPage` con upload drag-and-drop + preview + confirmación
- [x] 3.4 Manejar estados: loading (spinner en upload), error (archivo inválido), empty (sin datos)
- [x] 3.5 Integrar ruta `/academico/:materiaId/:cohorteId/calificaciones` con ProtectedRoute `calificaciones:importar`

## 4. Umbral, atrasados y ranking

- [x] 4.1 Crear `useUmbral` con GET/PUT umbral
- [x] 4.2 Crear `UmbralConfig` con slider input porcentaje 0-100
- [x] 4.3 Crear `useAtrasados` con GET atrasados
- [x] 4.4 Crear `AtrasadosTable` con tabla filtrable por nombre y actividad
- [x] 4.5 Crear `useRanking` con GET ranking
- [x] 4.6 Crear `RankingTable` ordenada por actividades aprobadas
- [x] 4.7 Crear `AtrasadosPage` que combina umbral + tabla atrasados + ranking
- [x] 4.8 Integrar ruta `/academico/:materiaId/:cohorteId/atrasados`

## 5. Notas finales y reportes rápidos

- [x] 5.1 Crear `useNotasFinales` con GET notas-finales
- [x] 5.2 Crear `NotasFinalesTable` con cálculo de nota final por alumno
- [x] 5.3 Crear `NotasFinalesPage` con tabla + métricas resumen
- [x] 5.4 Integrar ruta `/academico/:materiaId/:cohorteId/notas-finales`

## 6. Entregas sin corregir

- [x] 6.1 Crear `useEntregasSinCorregir` con GET entregas + POST subir reporte
- [x] 6.2 Crear `EntregasPage` con upload de reporte + tabla de entregas pendientes
- [x] 6.3 Implementar export CSV client-side con Blob download
- [x] 6.4 Integrar ruta `/academico/:materiaId/:cohorteId/entregas`

## 7. Comunicación con alumnos atrasados

- [x] 7.1 Crear `useComunicaciones` con POST preview, POST enviar, GET tracking
- [x] 7.2 Crear `ComunicacionPreview` side-sheet con preview de mensaje y navegación entre destinatarios
- [x] 7.3 Crear `ComunicacionTracking` con tabla de estados y polling cada 5s (refetchInterval)
- [x] 7.4 Crear `ComunicacionPage` que conecta selección de atrasados → preview → envío → tracking
- [x] 7.5 Integrar ruta `/academico/:materiaId/:cohorteId/comunicaciones`

## 8. Monitoreo de seguimiento (TUTOR/PROFESOR)

- [x] 8.1 Crear `useMonitoreo` con GET monitoreo
- [x] 8.2 Crear `MonitoreoPage` con tabla filtrable por alumno, actividad, mínimo cumplido
- [x] 8.3 Manejar estados: empty (sin datos), filtro sin resultados
- [x] 8.4 Integrar ruta `/academico/:materiaId/:cohorteId/monitoreo`

## 9. Tests

- [x] 9.1 Test: DashboardMetrics renderiza valores
- [x] 9.2 Test: ImportPreview renderiza actividades y confirma selección
- [x] 9.3 Test: AtrasadosTable renderiza alumnos con estados
- [x] 9.4 Test: RankingTable renderiza filas
- [x] 9.5 Test: NotasFinalesTable renderiza notas
- [x] 9.6 Test: EntregasSinCorregir renderiza tabla y botón export
- [x] 9.7 Test: ComunicacionPreview navega entre destinatarios
- [x] 9.8 Test: ComunicacionTracking muestra resumen final
- [x] 9.9 Test: MonitoreoAlumnos renderiza tabla

## 10. Integración y build

- [x] 10.1 Integrar todas las rutas en Router.tsx con lazy loading
- [x] 10.2 `npm run build` sin errores (tsc + vite)
- [x] 10.3 Verificar chunks separados por página
- [x] 10.4 Verificar que ProtectedRoute filtra correctamente permisos en Layout
