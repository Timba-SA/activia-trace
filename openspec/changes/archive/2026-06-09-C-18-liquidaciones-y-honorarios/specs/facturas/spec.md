## ADDED Requirements

### Requirement: Listar facturas

El sistema SHALL permitir consultar las facturas de docentes facturantes con filtros por período, docente y estado.

#### Scenario: Listar facturas con filtros
- **WHEN** se invoca `GET /api/facturas` con filtros opcionales (`periodo`, `usuario_id`, `estado`)
- **THEN** el sistema retorna 200 con la lista paginada de facturas

### Requirement: Cargar factura

El sistema SHALL permitir a FINANZAS cargar una factura presentada por un docente facturante.

#### Scenario: Carga exitosa
- **WHEN** se invoca `POST /api/facturas` con `usuario_id`, `periodo`, `detalle`, y `referencia_archivo`
- **THEN** el sistema crea un registro Factura con estado `Pendiente`
- **AND** establece `cargada_at` con la fecha/hora actual
- **AND** retorna 201 con la factura creada

#### Scenario: Carga con docente no facturante
- **WHEN** se invoca `POST /api/facturas` para un docente con `modalidad_cobro != "factura"`
- **THEN** el sistema retorna 422 con mensaje indicando que el docente no está configurado como facturante

### Requirement: Cambiar estado de factura

El sistema SHALL permitir a FINANZAS cambiar el estado de una factura entre Pendiente y Abonada.

#### Scenario: Abonar factura pendiente
- **WHEN** se invoca `PATCH /api/facturas/{id}/estado` con `estado = "Abonada"` para una factura en estado `Pendiente`
- **THEN** el sistema cambia el estado a `Abonada`
- **AND** establece `abonada_at` con la fecha/hora actual
- **AND** retorna 200 con la factura actualizada

#### Scenario: Reabrir factura abonada
- **WHEN** se invoca `PATCH /api/facturas/{id}/estado` con `estado = "Pendiente"` para una factura en estado `Abonada`
- **THEN** el sistema cambia el estado a `Pendiente`
- **AND** establece `abonada_at = NULL`
- **AND** retorna 200 con la factura actualizada

#### Scenario: Factura no encontrada
- **WHEN** se invoca `PATCH /api/facturas/{id}/estado` con un ID inexistente
- **THEN** el sistema retorna 404
