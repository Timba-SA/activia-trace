## Context

El frontend actual tiene módulos para académico (C-22) y coordinación (C-23). C-24 agrega los módulos de FINANZAS y ADMIN consumiendo APIs existentes del backend (C-06, C-07, C-18, C-19). Ambas features siguen el mismo patrón arquitectónico que C-22 y C-23.

## Goals / Non-Goals

**Goals:**
- Feature FINANZAS: liquidaciones, grilla salarial, facturas
- Feature ADMIN: estructura académica, usuarios, auditoría
- Consumir endpoints backend existentes sin cambios en API
- Tests ≥80% coverage en páginas y componentes nuevos

**Non-Goals:**
- No se modifica backend ni se agregan endpoints
- No se implementa lógica de negocio (solo presentación)
- No se toca el módulo de académico ni coordinación

## Decisions

1. **Módulo independiente `finanzas/` y `admin/`** en lugar de meter dentro de `coordinacion/`. Son dominios distintos con permisos propios.
2. **Patrón consistente con C-22/C-23**: types → services/api.ts → hooks/useModule.ts → pages/ → Router.tsx. Sin componentes intermedios (pages autocontenidas).
3. **Liquidaciones con tabs de segmentación**: General / NEXO / Factura como tabs visibles, no como filtros separados, para que el usuario entienda la segmentación conceptual.
4. **Auditoría con dashboard de métricas + log**: Dos vistas separadas (dashboard con KPIs, log con filtros) en una misma página con tabs.
5. **Lazy-loading** igual que el resto: cada página importada con `lazy()`.

## Risks / Trade-offs

- [Riesgo] C-18 backend marcado como pendiente pero implementado → verificar que endpoints respondan correctamente en integración.
- [Trade-off] Pages autocontenidas (sin componentes separados) mantiene LOC bajo pero duplica lógica de UI si se reusa. Se justifica porque cada feature tiene UI única.
