## Context

activia-trace necesita un módulo de liquidaciones y honorarios para que FINANZAS calcule, cierre y audite pagos docentes mensuales. Actualmente no existe este módulo; FINANZAS opera fuera del sistema. Se construye como 5 modelos nuevos, 2 routers, un servicio de cálculo con algoritmo reglado (RN-21 a RN-38), y ABM de grilla salarial con vigencia.

Depende de `C-07` (usuarios + asignaciones) para resolver docentes activos y sus comisiones por cohorte. La modalidad de pago del docente (facturante vs. relación de dependencia) se lee del perfil de Usuario (`modalidad_cobro`).

## Goals / Non-Goals

**Goals:**
- Liquidación automática por (cohorte × mes): base por rol + plus por grupo con tope
- Cierre inmutable (RN-22): una vez cerrada, no se modifica
- Grilla salarial versionada con vigencia `desde/hasta` (RN-31)
- Gestión de facturas de docentes facturantes con estados Pendiente/Abonada
- Segmentación contable: general, NEXO, facturantes con KPIS separados (RN-36/RN-38)
- Todos los endpoints protegidos con permisos `liquidaciones:*`
- Auditoría del cierre de liquidación (`LIQUIDACION_CERRAR`)

**Non-Goals:**
- No se implementa integración bancaria ni generación de órdenes de pago
- No se implementa cálculo automático de cargas sociales ni retenciones
- No se implementa workflow de aprobación multi-paso (solo cierre one-shot)
- No se calculan liquidaciones retroactivas (solo período corriente)
- No se implementa frontend (es C-24)

## Decisions

### D1 — Models: 5 entidades con soft-delete y tenant_id

Siguiendo el patrón de `C-02`. Todas heredan del mixin base con `id` (UUID), `tenant_id`, `created_at`, `updated_at`, `deleted_at`.

| Modelo | PK | FK clave | Atributos de negocio |
|--------|-----|----------|----------------------|
| SalarioBase | UUID | tenant_id | rol (enum), monto (decimal), desde (date), hasta (date nullable) |
| SalarioPlus | UUID | tenant_id | grupo (text), rol (enum), descripcion, monto, tope_acumulacion (int nullable), desde, hasta |
| MateriaGrupoPlus | UUID | tenant_id, materia_id | grupo (text), desde, hasta |
| Liquidacion | UUID | tenant_id, cohorte_id, usuario_id | periodo, rol, comisiones (JSONB), monto_base, monto_plus, total, es_nexo, excluido_por_factura, estado |
| Factura | UUID | tenant_id, usuario_id | periodo, detalle, referencia_archivo, tamano_kb, estado, cargada_at, abonada_at |

`comisiones` en Liquidacion es JSONB: lista de textos con los grupos/comisiones que generaron plus, para auditoría.

**Justificación**: JSONB para comisiones evita una tabla puente sin pérdida de auditoría (el detalle se congela al cerrar). El resto sigue el modelo estándar del proyecto.

### D2 — Cálculo de liquidación: algoritmo en LiquidacionService

flujo:

1. `POST /api/liquidaciones/calcular` recibe `cohorte_id` y `periodo` (AAAA-MM).
2. LiquidacionService.calcular():
   a. Obtener **todas las Asignacion activas** para la cohorte en el período (usuarios con rol docente en esa cohorte).
   b. Por cada docente:
      - Resolver **rol vigente** desde su Asignacion principal.
      - Buscar **SalarioBase** con `rol = docente.rol AND desde <= periodo <= hasta`. Si no existe → error.
      - Obtener **materias asignadas** al docente en esa cohorte.
      - Por cada materia, buscar **MateriaGrupoPlus** vigente (`desde <= periodo <= hasta`).
      - Agrupar materias por `grupo`.
      - Por cada grupo, buscar **SalarioPlus** vigente (`grupo, rol, desde <= periodo <= hasta`).
      - `N_efectivas = MIN(cantidad_materias_en_grupo, tope_acumulacion)` si tope no es NULL, sino `cantidad_materias_en_grupo`.
      - `monto_plus_parcial = plus.monto * N_efectivas`.
      - `monto_plus_total = Σ monto_plus_parcial`.
      - Si `usuario.modalidad_cobro == "factura"` → `excluido_por_factura = true`.
      - Si `rol == NEXO` → `es_nexo = true`.
      - `total = monto_base + monto_plus_total`.
   c. Crear registros Liquidacion para cada docente con estado `Abierta`.
   d. Devolver lista de liquidaciones creadas.

**Justificación**: El cálculo es puramente servicio (sin SQL en services), usando repositories para cada modelo. Esto sigue el flujo unidireccional (Router → Service → Repository → Model).

### D3 — Cierre inmutable con validación

`POST /api/liquidaciones/{id}/cerrar`:
1. Verificar que la liquidación existe y `estado == "Abierta"`.
2. Verificar que no haya sido cerrada previamente (idempotencia: si ya está Cerrada → 409 Conflict).
3. Transicionar `estado = "Cerrada"`.
4. Registrar auditoría: código `LIQUIDACION_CERRAR`, actor, detalle JSON con `{liquidacion_id, periodo, total, cohorte_id}`.
5. Devolver Liquidacion actualizada.

### D4 — 2 routers con permisos `liquidaciones:*`

| Router | Endpoint | Método | Permiso |
|--------|----------|--------|---------|
| `/api/liquidaciones/` | `/calcular` | POST | `liquidaciones:calcular` |
| | `/` | GET | `liquidaciones:ver` |
| | `/{id}` | GET | `liquidaciones:ver` |
| | `/{id}/cerrar` | POST | `liquidaciones:cerrar` |
| | `/historial` | GET | `liquidaciones:ver` |
| | `/exportar` | POST | `liquidaciones:exportar` |
| | `/salarios-base` | GET | `liquidaciones:configurar-salarios` |
| | `/salarios-base` | POST | `liquidaciones:configurar-salarios` |
| | `/salarios-base/{id}` | PUT | `liquidaciones:configurar-salarios` |
| | `/salarios-base/{id}` | DELETE | `liquidaciones:configurar-salarios` |
| | `/plus` | GET | `liquidaciones:configurar-salarios` |
| | `/plus` | POST | `liquidaciones:configurar-salarios` |
| | `/plus/{id}` | PUT | `liquidaciones:configurar-salarios` |
| | `/plus/{id}` | DELETE | `liquidaciones:configurar-salarios` |
| | `/materias-grupo` | GET | `liquidaciones:configurar-salarios` |
| | `/materias-grupo` | POST | `liquidaciones:configurar-salarios` |
| | `/materias-grupo/{id}` | PUT | `liquidaciones:configurar-salarios` |
| | `/materias-grupo/{id}` | DELETE | `liquidaciones:configurar-salarios` |
| `/api/facturas/` | `/` | GET | `liquidaciones:ver` |
| | `/` | POST | `liquidaciones:gestionar-facturas` |
| | `/{id}/estado` | PATCH | `liquidaciones:gestionar-facturas` |

**Justificación**: Los endpoints de grilla salarial se anidan bajo `/api/liquidaciones/` porque conceptualmente son configuración de la liquidación, no un módulo separado. Las facturas tienen router propio porque su ciclo de vida (Pendiente → Abonada) es independiente de la liquidación general.

### D5 — 6 nuevos permisos en el catálogo RBAC

| Permiso | Asignado a | Uso |
|---------|-----------|-----|
| `liquidaciones:calcular` | FINANZAS | Disparar el cálculo del período |
| `liquidaciones:ver` | FINANZAS, ADMIN | Ver liquidaciones, historial, facturas |
| `liquidaciones:cerrar` | FINANZAS | Cerrar (inmutabilizar) una liquidación |
| `liquidaciones:exportar` | FINANZAS | Exportar planilla de liquidación |
| `liquidaciones:configurar-salarios` | FINANZAS | ABM de grilla salarial y mapeo materia↔grupo |
| `liquidaciones:gestionar-facturas` | FINANZAS | Cargar y cambiar estado de facturas |

Se agregan al seed del rol FINANZAS en la próxima migración.

### D6 — Migración única: 5 tablas

Una sola migración Alembic (`0NN_liquidaciones`) con todas las tablas:

```sql
CREATE TABLE salario_base (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenant(id),
  rol VARCHAR(20) NOT NULL,
  monto NUMERIC(12,2) NOT NULL,
  desde DATE NOT NULL,
  hasta DATE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);
CREATE UNIQUE INDEX uq_salario_base_vigente ON salario_base (tenant_id, rol, desde) WHERE deleted_at IS NULL;

CREATE TABLE salario_plus (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenant(id),
  grupo VARCHAR(50) NOT NULL,
  rol VARCHAR(20) NOT NULL,
  descripcion TEXT,
  monto NUMERIC(12,2) NOT NULL,
  tope_acumulacion INTEGER,
  desde DATE NOT NULL,
  hasta DATE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);

CREATE TABLE materia_grupo_plus (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenant(id),
  materia_id UUID NOT NULL REFERENCES materia(id),
  grupo VARCHAR(50) NOT NULL,
  desde DATE NOT NULL,
  hasta DATE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);
CREATE UNIQUE INDEX uq_materia_grupo_vigente ON materia_grupo_plus (tenant_id, materia_id, grupo, desde) WHERE deleted_at IS NULL;

CREATE TABLE liquidacion (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenant(id),
  cohorte_id UUID NOT NULL REFERENCES cohorte(id),
  periodo VARCHAR(7) NOT NULL,
  usuario_id UUID NOT NULL REFERENCES usuario(id),
  rol VARCHAR(20) NOT NULL,
  comisiones JSONB NOT NULL DEFAULT '[]',
  monto_base NUMERIC(12,2) NOT NULL,
  monto_plus NUMERIC(12,2) NOT NULL DEFAULT 0,
  total NUMERIC(12,2) NOT NULL,
  es_nexo BOOLEAN NOT NULL DEFAULT FALSE,
  excluido_por_factura BOOLEAN NOT NULL DEFAULT FALSE,
  estado VARCHAR(10) NOT NULL DEFAULT 'Abierta',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);
CREATE UNIQUE INDEX uq_liquidacion_periodo ON liquidacion (tenant_id, cohorte_id, periodo, usuario_id) WHERE deleted_at IS NULL;

CREATE TABLE factura (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenant(id),
  usuario_id UUID NOT NULL REFERENCES usuario(id),
  periodo VARCHAR(7) NOT NULL,
  detalle TEXT,
  referencia_archivo TEXT NOT NULL,
  tamano_kb NUMERIC(10,2),
  estado VARCHAR(10) NOT NULL DEFAULT 'Pendiente',
  cargada_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  abonada_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);
```

**Rollback**: `DROP TABLE factura, liquidacion, materia_grupo_plus, salario_plus, salario_base;`

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|-----------|
| El cálculo puede ser lento con muchos docentes × comisiones | El cálculo es on-demand (no en tiempo real); se puede optimizar con queries agregadas si es necesario |
| La exclusión por factura depende del campo `modalidad_cobro` en Usuario | Validar al calcular que el campo exista; si falta, asumir relación de dependencia |
| El cierre no es transaccional si hay múltiples liquidaciones abiertas del mismo período | Cada liquidación se cierra individualmente; el cálculo crea una por docente |
| Los permisos `liquidaciones:*` son 6 nuevos; hay que seedearlos al rol FINANZAS | Incluir seed en la misma migración que crea las tablas |
| La unicidad de `salario_base` por (tenant_id, rol, desde) puede fallar si hay overlaps | Validar en servicio antes de insertar; rechazar overlaps con 409 |
