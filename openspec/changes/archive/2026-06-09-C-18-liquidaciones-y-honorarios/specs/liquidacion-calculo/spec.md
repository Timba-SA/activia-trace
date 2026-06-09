## ADDED Requirements

### Requirement: Calcular liquidación del período

El sistema SHALL calcular la liquidación de honorarios para todos los docentes de una cohorte en un período mensual, combinando salario base vigente por rol con plus variables por grupo de materias.

**Validaciones previas:**
- El período DEBE tener formato `AAAA-MM`.
- La cohorte DEBE existir y estar activa.
- Al menos un docente DEBE tener asignaciones activas en la cohorte para el período.

#### Scenario: Cálculo exitoso con base y plus
- **WHEN** se invoca `POST /api/liquidaciones/calcular` con `cohorte_id` y `periodo` válidos
- **THEN** el sistema crea registros Liquidacion en estado `Abierta` para cada docente con asignaciones activas
- **AND** cada liquidación contiene `monto_base` (del SalarioBase vigente según rol), `monto_plus` (suma de plus aplicables), y `total = monto_base + monto_plus`
- **AND** el endpoint retorna 201 con la lista de liquidaciones creadas

#### Scenario: Cálculo con docente sin salario base vigente
- **WHEN** se invoca el cálculo y un docente tiene un rol sin SalarioBase vigente en el período
- **THEN** el sistema retorna 422 con detalle del docente y rol afectado

#### Scenario: Cálculo con docente facturante
- **WHEN** el cálculo incluye un docente con `modalidad_cobro = "factura"`
- **THEN** su liquidación se crea con `excluido_por_factura = true`
- **AND** el total se calcula igual pero se marca como excluido

#### Scenario: Cálculo con rol NEXO
- **WHEN** el cálculo incluye un docente con rol NEXO
- **THEN** su liquidación se crea con `es_nexo = true`
- **AND** el total se suma al consolidado general

#### Scenario: Cálculo con plus y tope de acumulación
- **WHEN** un docente tiene 5 comisiones en un grupo cuyo SalarioPlus tiene `tope_acumulacion = 3`
- **THEN** el `monto_plus` se calcula como `plus.monto × 3` (no 5)
- **AND** el campo `comisiones` JSONB refleja las 5 comisiones pero el cómputo respeta el tope

#### Scenario: Cálculo con plus sin tope
- **WHEN** un docente tiene N comisiones en un grupo cuyo SalarioPlus tiene `tope_acumulacion = NULL`
- **THEN** el `monto_plus` se calcula como `plus.monto × N`

#### Scenario: Período duplicado
- **WHEN** se invoca el cálculo para un (cohorte, período) que ya tiene liquidaciones creadas
- **THEN** el sistema retorna 409 Conflict

### Requirement: Ver liquidaciones

El sistema SHALL permitir consultar las liquidaciones con filtros por cohorte, período y docente.

#### Scenario: Listar liquidaciones con filtros
- **WHEN** se invoca `GET /api/liquidaciones` con `cohorte_id`, `periodo`, y opcionalmente `usuario_id`
- **THEN** el sistema retorna 200 con la lista paginada de liquidaciones que coinciden

#### Scenario: Detalle individual de liquidación
- **WHEN** se invoca `GET /api/liquidaciones/{id}` con un ID válido
- **THEN** el sistema retorna 200 con el detalle completo de la liquidación (monto_base, monto_plus, total, rol, comisiones, estado, es_nexo, excluido_por_factura)

#### Scenario: Liquidación no encontrada
- **WHEN** se invoca `GET /api/liquidaciones/{id}` con un ID inexistente
- **THEN** el sistema retorna 404

### Requirement: Cerrar liquidación

El sistema SHALL permitir cerrar (inmutabilizar) una liquidación en estado `Abierta`.

#### Scenario: Cierre exitoso
- **WHEN** se invoca `POST /api/liquidaciones/{id}/cerrar` para una liquidación en estado `Abierta`
- **THEN** el sistema cambia su estado a `Cerrada`
- **AND** registra auditoría con código `LIQUIDACION_CERRAR`
- **AND** retorna 200 con la liquidación actualizada

#### Scenario: Cierre de liquidación ya cerrada
- **WHEN** se invoca `POST /api/liquidaciones/{id}/cerrar` para una liquidación en estado `Cerrada`
- **THEN** el sistema retorna 409 Conflict

#### Scenario: Cierre de liquidación inexistente
- **WHEN** se invoca `POST /api/liquidaciones/{id}/cerrar` con un ID inexistente
- **THEN** el sistema retorna 404

#### Scenario: Inmutabilidad post-cierre
- **WHEN** se intenta modificar una liquidación cerrada (recalcular, actualizar)
- **THEN** el sistema rechaza la operación con 409 Conflict

### Requirement: Historial de liquidaciones cerradas

El sistema SHALL exponer el historial de liquidaciones cerradas para consulta auditora.

#### Scenario: Consultar historial
- **WHEN** se invoca `GET /api/liquidaciones/historial` con filtros opcionales (cohorte, período, docente)
- **THEN** el sistema retorna 200 con liquidaciones en estado `Cerrada` paginadas

### Requirement: Exportar planilla de liquidación

El sistema SHALL permitir exportar las liquidaciones de un período a un archivo descargable.

#### Scenario: Exportación exitosa
- **WHEN** se invoca `POST /api/liquidaciones/exportar` con `cohorte_id` y `periodo`
- **THEN** el sistema genera un archivo con los datos de liquidación del período
- **AND** retorna el archivo como descarga
