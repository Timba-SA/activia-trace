## Why

El sistema necesita gestionar la liquidación de honorarios docentes: calcular, cerrar y auditar pagos mensuales por (cohorte × mes) con base salarial fija por rol, plus variables por grupo de materias con tope configurable, y flujo separado para docentes que facturan. Sin este módulo, FINANZAS debe operar fuera del sistema, perdiendo trazabilidad y control.

## What Changes

- 5 nuevos modelos de dominio: SalarioBase, SalarioPlus, MateriaGrupoPlus, Liquidacion, Factura
- 2 nuevos routers: `/api/liquidaciones/*` y `/api/facturas/*` con guards `liquidaciones:*`
- Algoritmo de cálculo: Total = Base(rol, período) + Σ(Plus × MIN(N_comisiones, tope_acumulacion))
- ABM de grilla salarial (F10.4): salario base por rol + plus por (grupo, rol) con vigencia `desde/hasta`
- Cierre de liquidación con inmutabilidad (RN-22)
- Gestión de facturas de docentes facturantes (F10.5): carga, cambio de estado Pendiente/Abonada
- Segmentación contable: general / NEXO / factura con KPIs separados (F10.6, RN-36/RN-38)
- Auditoría: códigos `LIQUIDACION_CERRAR` en AuditLog
- 6 nuevos permisos: `liquidaciones:calcular`, `liquidaciones:ver`, `liquidaciones:cerrar`, `liquidaciones:exportar`, `liquidaciones:configurar-salarios`, `liquidaciones:gestionar-facturas`
- 1 migración Alembic con 5 tablas
- Tests: cálculo con tope, cierre inmutable, mapeo materia↔grupo, exclusión facturantes, segmentación NEXO

## Capabilities

### New Capabilities
- `liquidacion-calculo`: cálculo automático de liquidación por (cohorte × mes) con base vigente + plus con tope, vista previa, cierre inmutable, historial y exportación
- `grilla-salarial`: ABM de salario base por rol y plus por (grupo, rol) con vigencia temporal desde/hasta
- `facturas`: gestión de facturas de docentes facturantes — carga, consulta, cambio de estado Pendiente/Abonada

### Modified Capabilities

None — this is a new module.

## Impact

- **DB**: 5 nuevas tablas (`salario_base`, `salario_plus`, `materia_grupo_plus`, `liquidacion`, `factura`) + 1 migración
- **API**: 2 nuevos routers (`/api/liquidaciones/`, `/api/facturas/`) con ~10 endpoints, todos protegidos con `liquidaciones:*`
- **Permissions**: 6 nuevos permisos asignables al rol FINANZAS
- **Audit**: nuevo código `LIQUIDACION_CERRAR` en el catálogo de acciones
- **Dependencies**: requiere `C-07` (usuarios + asignaciones) para resolución de docentes y comisiones
