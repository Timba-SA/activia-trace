# Spec: Facturas — Gestión de Facturas

## ADDED Requirements

### Requirement: Listar facturas
The system MUST display a list of facturas fetched from GET /api/facturas with filter controls for periodo, usuario_id, and estado. Each row in the list MUST show: usuario_id, periodo, detalle, referencia_archivo, estado, cargada_at, abonada_at. The list MUST be paginated.

#### Scenario: List facturas with filters
- **WHEN** the user navigates to the Facturas section and optionally applies periodo, usuario_id, or estado filters
- **THEN** the system MUST fetch from GET /api/facturas?periodo={p}&usuario_id={id}&estado={e}, render a paginated table with all specified columns, and reflect the applied filters in the URL query string

#### Scenario: List facturas without filters
- **WHEN** the user navigates to the Facturas section without applying any filters
- **THEN** the system MUST fetch all facturas from GET /api/facturas and render the first page of results

#### Scenario: Empty list when no facturas match
- **WHEN** the applied filters return zero results from GET /api/facturas
- **THEN** the system MUST display an empty-state message indicating no facturas match the current filters

### Requirement: Crear factura
The system MUST provide a form to create a new factura via POST /api/facturas with fields: usuario_id, periodo, detalle, referencia_archivo, and tamano_kb. The system MUST validate that usuario_id is a valid user, periodo is a valid period string, and tamano_kb is a positive number.

#### Scenario: Create factura successfully
- **WHEN** the user fills in all required fields (usuario_id, periodo, detalle) and optionally referencia_archivo and tamano_kb, and submits the form
- **THEN** the system MUST POST to /api/facturas with the form data, and upon success MUST add the new factura to the list and show a success notification

#### Scenario: Create factura with missing required fields
- **WHEN** the user submits the form without usuario_id, periodo, or detalle
- **THEN** the system MUST show inline validation errors on each missing required field and NOT submit the form

#### Scenario: Create factura with invalid tamano_kb
- **WHEN** the user submits the form with tamano_kb set to zero or a negative number
- **THEN** the system MUST show an inline validation error on tamano_kb indicating it must be a positive number

### Requirement: Cambiar estado de factura
The system MUST provide an action to change a factura's estado via PATCH /api/facturas/{id}/estado with body {"estado": "<new_state>"}. The system MUST show the available state transitions based on the current estado and confirm before applying.

#### Scenario: Change factura estado successfully
- **WHEN** the user selects a new estado for a factura from the available transitions and confirms
- **THEN** the system MUST PATCH /api/facturas/{id}/estado with {"estado": "<new_state>"}, and upon success MUST update the row with the new estado and timestamps and show a success notification

#### Scenario: Change factura estado with invalid transition
- **WHEN** the user attempts to change to an estado that is not a valid transition from the current estado
- **THEN** the system MUST display the API error message and keep the row in its current estado
