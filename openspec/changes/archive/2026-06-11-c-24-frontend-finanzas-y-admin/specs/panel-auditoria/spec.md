# Spec: Panel de Auditoría — Dashboard de Métricas y Últimas Acciones

## ADDED Requirements

### Requirement: Dashboard de métricas
The system MUST display a KPI dashboard with metrics fetched from four endpoints: GET /api/auditoria/metricas/acciones-por-dia, GET /api/auditoria/metricas/por-docente, GET /api/auditoria/metricas/por-materia, and GET /api/auditoria/metricas/comunicaciones. The dashboard MUST provide filter controls for desde, hasta, materia_id, and actor_id. Each metric section MUST be displayed as a KPI card or chart with the metric name and value clearly visible.

#### Scenario: Display acciones-por-dia metric
- **WHEN** the user opens the Auditoría dashboard
- **THEN** the system MUST fetch from GET /api/auditoria/metricas/acciones-por-dia and render a chart or card showing the count of actions per day

#### Scenario: Display por-docente metric
- **WHEN** the user opens the Auditoría dashboard
- **THEN** the system MUST fetch from GET /api/auditoria/metricas/por-docente and render a chart or KPI showing action counts grouped by docente

#### Scenario: Display por-materia metric
- **WHEN** the user opens the Auditoría dashboard
- **THEN** the system MUST fetch from GET /api/auditoria/metricas/por-materia and render a chart or KPI showing action counts grouped by materia

#### Scenario: Display comunicaciones metric
- **WHEN** the user opens the Auditoría dashboard
- **THEN** the system MUST fetch from GET /api/auditoria/metricas/comunicaciones and render a chart or KPI showing communication-related metrics

#### Scenario: Filter all metrics by date range
- **WHEN** the user sets desde and hasta date filters on the dashboard
- **THEN** the system MUST append ?desde={d}&hasta={h} to all four metric endpoint requests and update all visible charts and KPIs accordingly

#### Scenario: Filter metrics by materia_id and actor_id
- **WHEN** the user selects a materia and/or an actor from the filter controls
- **THEN** the system MUST append &materia_id={m}&actor_id={a} to the relevant metric endpoint requests and update the affected charts

#### Scenario: Loading state while metrics load
- **WHEN** the metrics are being fetched
- **THEN** the system MUST show a loading skeleton or spinner for each metric section that is still loading

#### Scenario: Error state when a metric endpoint fails
- **WHEN** one of the metric endpoints returns a 4xx or 5xx error
- **THEN** the system MUST display an error state specific to that metric section without affecting other sections that loaded successfully

### Requirement: Últimas acciones
The system MUST display a paginated table of recent audit actions fetched from GET /api/auditoria/ultimas-acciones. The table MUST support filters for accion, actor_id, materia_id, desde, and hasta. The system MUST cap results at 500 records maximum and display the remaining count when the cap is reached.

#### Scenario: View últimas acciones without filters
- **WHEN** the user navigates to the "Últimas Acciones" tab in the Auditoría section
- **THEN** the system MUST fetch from GET /api/auditoria/ultimas-acciones and render a paginated table with columns for timestamp, accion, actor, materia, and details

#### Scenario: Filter últimas acciones
- **WHEN** the user applies filters for accion, actor_id, materia_id, desde, and/or hasta
- **THEN** the system MUST fetch from GET /api/auditoria/ultimas-acciones?accion={a}&actor_id={x}&materia_id={m}&desde={d}&hasta={h} and render the filtered results in a paginated table

#### Scenario: Paginate through últimas acciones
- **WHEN** the filtered results span multiple pages
- **THEN** the system MUST show pagination controls and fetch the requested page via GET /api/auditoria/ultimas-acciones?page={n}

#### Scenario: Results capped at 500 records
- **WHEN** the total matching records exceed 500
- **THEN** the system MUST display a notice indicating "Mostrando 500 de X registros" and paginate only within the first 500 results

#### Scenario: Empty results for últimas acciones
- **WHEN** the applied filters return zero results
- **THEN** the system MUST display an empty-state message indicating no audit actions match the current filters
