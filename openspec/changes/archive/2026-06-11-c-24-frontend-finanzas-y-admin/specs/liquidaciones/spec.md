# Spec: Liquidaciones — Módulo de Liquidaciones de Honorarios

## ADDED Requirements

### Requirement: Vista de liquidaciones del período
The system MUST display a table of liquidaciones for a given cohorte and periodo, where each row shows usuario_id, rol, comisiones, monto_base, monto_plus, total, es_nexo, and excluido_por_factura. The system MUST provide filter controls for cohorte_id and periodo. The system MUST segment the view into three tabs: General (all records), NEXO (records where es_nexo is true), and Factura (records where excluido_por_factura is true). The system MUST fetch data from GET /api/liquidaciones/ with cohorte_id and periodo query parameters.

#### Scenario: Display liquidaciones for a selected cohorte and periodo
- **WHEN** the user selects a cohorte and a periodo
- **THEN** the system MUST fetch liquidaciones from GET /api/liquidaciones/?cohorte_id={id}&periodo={periodo} and render a table with columns usuario_id, rol, comisiones, monto_base, monto_plus, total, es_nexo, excluido_por_factura

#### Scenario: Segment into General / NEXO / Factura tabs
- **WHEN** the liquidaciones table is displayed
- **THEN** the system MUST show three tabs: "General" showing all records, "NEXO" filtering by es_nexo=true, and "Factura" filtering by excluido_por_factura=true, with the active tab clearly highlighted

#### Scenario: Empty state when no liquidaciones exist
- **WHEN** GET /api/liquidaciones/ returns an empty array
- **THEN** the system MUST display an empty-state message indicating no liquidaciones exist for the selected cohorte and periodo

### Requirement: Calcular liquidación
The system MUST provide a "Calcular" button that sends a POST request to /api/liquidaciones/calcular with cohorte_id and periodo. The system MUST show loading state during the request and display the result (success or error) upon completion.

#### Scenario: Calculate liquidaciones successfully
- **WHEN** the user clicks "Calcular" with a valid cohorte_id and periodo
- **THEN** the system MUST POST to /api/liquidaciones/calcular with body {"cohorte_id": "...", "periodo": "..."} and upon success MUST refresh the liquidaciones table and show a success notification

#### Scenario: Calculate liquidaciones with validation error
- **WHEN** the user clicks "Calcular" without selecting a cohorte or periodo
- **THEN** the system MUST disable the button and show an inline validation message requesting both fields

#### Scenario: Calculate liquidaciones with server error
- **WHEN** the POST /api/liquidaciones/calcular returns a 4xx or 5xx error
- **THEN** the system MUST display the error message from the API response and keep the table in its previous state

### Requirement: Cerrar liquidación
The system MUST provide a "Cerrar" action per liquidación that sends a POST request to /api/liquidaciones/{id}/cerrar. The system MUST confirm the action before executing and update the row state on success.

#### Scenario: Close a liquidación successfully
- **WHEN** the user clicks "Cerrar" on a liquidación row and confirms the action
- **THEN** the system MUST POST to /api/liquidaciones/{id}/cerrar, and upon success MUST update the row to reflect the closed state and show a success notification

#### Scenario: Close a liquidación that is already closed
- **WHEN** the user attempts to close a liquidación that returns a 409 Conflict
- **THEN** the system MUST display the API error message and keep the row unchanged

### Requirement: Historial de liquidaciones
The system MUST provide a historial view fetched from GET /api/liquidaciones/historial with filters for cohorte_id and periodo. The historial MUST display past liquidaciones with their closure status and timestamps.

#### Scenario: View historial with filters
- **WHEN** the user navigates to the historial tab and applies cohorte_id and/or periodo filters
- **THEN** the system MUST fetch from GET /api/liquidaciones/historial?cohorte_id={id}&periodo={periodo} and render a read-only table with historical liquidaciones data

#### Scenario: Historial without filters
- **WHEN** the user opens the historial view without applying filters
- **THEN** the system MUST fetch all available historial records and display them in a paginated table

### Requirement: Exportar liquidaciones a CSV
The system MUST provide an "Exportar CSV" button that POSTs to /api/liquidaciones/exportar with the current filters (cohorte_id, periodo). The system MUST trigger a file download on success.

#### Scenario: Export CSV successfully
- **WHEN** the user clicks "Exportar CSV" with active cohorte and periodo filters
- **THEN** the system MUST POST to /api/liquidaciones/exportar with body {"cohorte_id": "...", "periodo": "..."} and trigger a browser download of the resulting CSV file

#### Scenario: Export CSV without filters
- **WHEN** the user clicks "Exportar CSV" without selecting a cohorte or periodo
- **THEN** the system MUST show an inline validation message requiring both filters before export
