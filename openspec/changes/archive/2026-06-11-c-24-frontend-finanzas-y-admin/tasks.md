## 1. Module Structure & Routes

- [x] 1.1 Create `features/finanzas/` and `features/admin/` directories with types, services, hooks, pages
- [x] 1.2 Add lazy-load imports and routes in Router.tsx for `/liquidaciones`, `/grilla-salarial`, `/facturas`, `/admin/carreras`, `/admin/cohortes`, `/admin/materias`, `/admin/usuarios`, `/admin/auditoria`
- [x] 1.3 Add nav entries in Layout.tsx for Finanzas and Admin submenus

## 2. FINANZAS — Liquidaciones

- [x] 2.1 Define types: LiquidacionResponse, LiquidacionListResponse, LiquidacionCalcularRequest, LiquidacionHistorialResponse, ExportarRequest
- [x] 2.2 Add API functions: listarLiquidaciones, calcularLiquidacion, cerrarLiquidacion, historialLiquidaciones, exportarLiquidaciones
- [x] 2.3 Add hooks: useLiquidaciones, useCalcularLiquidacion, useCerrarLiquidacion, useHistorialLiquidaciones
- [x] 2.4 Create LiquidacionesPage with segmentación tabs (General / NEXO / Factura), tabla de liquidaciones, botón calcular, botón cerrar, historial, export

## 3. FINANZAS — Grilla Salarial

- [x] 3.1 Define types: SalarioBaseRequest/Response, SalarioPlusRequest/Response, MateriaGrupoPlusRequest/Response
- [x] 3.2 Add API functions for salarios-base CRUD, plus CRUD, materias-grupo CRUD
- [x] 3.3 Add hooks for each CRUD
- [x] 3.4 Create GrillaSalarialPage with 3 tabs: Salarios Base / Plus / Materia-Grupo. Each tab: table + create/edit/delete modals

## 4. FINANZAS — Facturas

- [x] 4.1 Define types: FacturaCreate, FacturaResponse, FacturaListResponse, FacturaEstadoUpdate
- [x] 4.2 Add API functions: listarFacturas, crearFactura, cambiarEstadoFactura
- [x] 4.3 Add hooks
- [x] 4.4 Create FacturasPage: tabla de facturas + botón crear + dropdown de estado

## 5. ADMIN — Estructura Académica

- [x] 5.1 Define types for Carrera, Cohorte, Materia (request/response/list response)
- [x] 5.2 Add API functions for carreras CRUD, cohortes CRUD, materias CRUD
- [x] 5.3 Add hooks
- [x] 5.4 Create CarrerasPage: ABM carreras
- [x] 5.5 Create CohortesPage: ABM cohortes filtrado por carrera
- [x] 5.6 Create MateriasPage: ABM materias filtrado por carrera

## 6. ADMIN — Usuarios

- [x] 6.1 Define types: UsuarioResponse, UsuarioListResponse, UsuarioDetalleResponse, UsuarioUpdateRequest
- [x] 6.2 Add API functions: listarUsuarios, obtenerUsuario, actualizarUsuario
- [x] 6.3 Add hooks
- [x] 6.4 Create UsuariosPage: tabla con filtros (nombre, apellido, email, legajo, is_active) + detalle expandible + edición

## 7. ADMIN — Auditoría

- [x] 7.1 Define types: MetricasAccionesPorDia, MetricaPorDocente, MetricaPorMateria, MetricaComunicacion, AuditLogResponse, AuditLogListResponse
- [x] 7.2 Add API functions for metricas endpoints and ultimas-acciones
- [x] 7.3 Add hooks
- [x] 7.4 Create AuditoriaPage with 2 tabs: Dashboard (KPIs, gráficos de métricas) y Log (tabla paginada con filtros)

## 8. Tests

- [x] 8.1 Write tests for LiquidacionesPage — 4 tests ✓
- [x] 8.2 Write tests for GrillaSalarialPage — 4 tests ✓
- [x] 8.3 Write tests for FacturasPage — 3 tests ✓
- [x] 8.4 Write tests for CarrerasPage, CohortesPage, MateriasPage — 3+3+3 = 9 tests ✓
- [x] 8.5 Write tests for UsuariosPage — 3 tests ✓
- [x] 8.6 Write tests for AuditoriaPage — 2 tests ✓
