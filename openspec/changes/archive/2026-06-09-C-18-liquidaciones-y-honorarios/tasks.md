## 1. Models

- [x] 1.1 Create `models/salario_base.py` — SalarioBase (id, tenant_id, rol, monto, desde, hasta, timestamps, soft delete)
- [x] 1.2 Create `models/salario_plus.py` — SalarioPlus (id, tenant_id, grupo, rol, descripcion, monto, tope_acumulacion nullable, desde, hasta, timestamps, soft delete)
- [x] 1.3 Create `models/materia_grupo_plus.py` — MateriaGrupoPlus (id, tenant_id, materia_id, grupo, desde, hasta, timestamps, soft delete)
- [x] 1.4 Create `models/liquidacion.py` — Liquidacion (id, tenant_id, cohorte_id, periodo, usuario_id, rol, comisiones JSONB, monto_base, monto_plus, total, es_nexo, excluido_por_factura, estado, timestamps, soft delete)
- [x] 1.5 Create `models/factura.py` — Factura (id, tenant_id, usuario_id, periodo, detalle, referencia_archivo, tamano_kb, estado, cargada_at, abonada_at, timestamps, soft delete)
- [x] 1.6 Register all models in `models/__init__.py`

## 2. Pydantic Schemas

- [x] 2.1 Create `schemas/salario_base.py` — SalarioBaseCreate, SalarioBaseUpdate, SalarioBaseResponse (extra='forbid')
- [x] 2.2 Create `schemas/salario_plus.py` — SalarioPlusCreate, SalarioPlusUpdate, SalarioPlusResponse
- [x] 2.3 Create `schemas/materia_grupo_plus.py` — MateriaGrupoPlusCreate, MateriaGrupoPlusUpdate, MateriaGrupoPlusResponse
- [x] 2.4 Create `schemas/liquidacion.py` — LiquidacionResponse, LiquidacionCalcularRequest (cohorte_id, periodo), LiquidacionCerrarResponse, LiquidacionHistorialResponse
- [x] 2.5 Create `schemas/factura.py` — FacturaCreate, FacturaEstadoUpdate, FacturaResponse
- [x] 2.6 Create `schemas/__init__.py` exports

## 3. Repositories

- [x] 3.1 Create `repositories/salario_base.py` — SalarioBaseRepository (find vigente por rol+periodo, CRUD, validar overlap vigencia)
- [x] 3.2 Create `repositories/salario_plus.py` — SalarioPlusRepository (find vigente por grupo+rol+periodo, CRUD)
- [x] 3.3 Create `repositories/materia_grupo_plus.py` — MateriaGrupoPlusRepository (find vigente por materia+periodo, CRUD, validar unicidad)
- [x] 3.4 Create `repositories/liquidacion.py` — LiquidacionRepository (find por filtros, find por id, find historial, create batch, update estado)
- [x] 3.5 Create `repositories/factura.py` — FacturaRepository (CRUD, cambio de estado)
- [x] 3.6 Register repos in `repositories/__init__.py`

## 4. Services

- [x] 4.1 Create `services/liquidacion_service.py` — LiquidacionService.calcular() con algoritmo completo (base vigente + plus con tope + exclusión facturantes + segmentación NEXO)
- [x] 4.2 Create `services/liquidacion_service.py` — cerrar() con inmutabilidad + auditoría (LIQUIDACION_CERRAR)
- [x] 4.3 Create `services/liquidacion_service.py` — exportar() generación de planilla
- [x] 4.4 Create `services/factura_service.py` — FacturaService (crear, cambiar estado, validar docente facturante)
- [x] 4.5 Create `services/grilla_service.py` — GrillaService (ABM SalarioBase, SalarioPlus, MateriaGrupoPlus con validación de vigencia y overlap)
- [x] 4.6 Register services in `services/__init__.py`

## 5. Permissions

- [x] 5.1 Add 6 new permissions to the RBAC seed: `liquidaciones:calcular`, `liquidaciones:ver`, `liquidaciones:cerrar`, `liquidaciones:exportar`, `liquidaciones:configurar-salarios`, `liquidaciones:gestionar-facturas`
- [x] 5.2 Assign all 6 permissions to role FINANZAS, and `liquidaciones:ver` to ADMIN

## 6. Routers

- [x] 6.1 Create `routers/liquidaciones.py` — POST /calcular (liquidaciones:calcular), GET / (liquidaciones:ver), GET /{id} (liquidaciones:ver), POST /{id}/cerrar (liquidaciones:cerrar), GET /historial (liquidaciones:ver), POST /exportar (liquidaciones:exportar)
- [x] 6.2 Add grilla salarial endpoints to `routers/liquidaciones.py` — CRUD /salarios-base, CRUD /plus, CRUD /materias-grupo (liquidaciones:configurar-salarios)
- [x] 6.3 Create `routers/facturas.py` — GET / (liquidaciones:ver), POST / (liquidaciones:gestionar-facturas), PATCH /{id}/estado (liquidaciones:gestionar-facturas)
- [x] 6.4 Register both routers in `app/main.py`

## 7. Migration

- [x] 7.1 Generate Alembic migration `017_liquidaciones` with 5 tables (salario_base, salario_plus, materia_grupo_plus, liquidacion, factura) + unique indexes + seed permissions for FINANZAS
- [x] 7.2 Run migration and verify tables created

## 8. Tests

- [ ] 8.1 Test: cálculo con salario base vigente por período
- [ ] 8.2 Test: cálculo con plus y tope_acumulacion (NULL y numérico)
- [ ] 8.3 Test: cálculo de total = base + plus
- [ ] 8.4 Test: cierre de liquidación (éxito y doble cierre 409)
- [ ] 8.5 Test: inmutabilidad post-cierre
- [ ] 8.6 Test: mapeo materia↔grupo vigente por período
- [ ] 8.7 Test: exclusión de docentes facturantes de liquidación general
- [ ] 8.8 Test: segmentación NEXO (es_nexo = true, suma al total)
- [ ] 8.9 Test: factura CRUD + cambio de estado Pendiente/Abonada
- [ ] 8.10 Test: permisos — FINANZAS puede, otros roles 403
- [ ] 8.11 Test: aislamiento multi-tenant en liquidaciones y facturas
- [ ] 8.12 Test: grilla salarial — overlap de vigencia rechazado (409)
