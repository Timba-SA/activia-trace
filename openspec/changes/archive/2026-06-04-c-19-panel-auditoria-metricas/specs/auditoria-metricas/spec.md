## ADDED Requirements

### Requirement: Metric — Acciones por día

The system SHALL provide `GET /api/auditoria/metricas/acciones-por-dia` returning an array of daily action counts. The endpoint SHALL support optional query parameters: `desde` (datetime), `hasta` (datetime), `materia_id` (UUID). Results SHALL be grouped by calendar date and ordered chronologically descending. The endpoint SHALL be guarded by `require_permission("auditoria:ver")` and SHALL scope results to the current tenant.

#### Scenario: Acciones por día returns daily counts

- **WHEN** a user with `auditoria:ver` sends GET to `/api/auditoria/metricas/acciones-por-dia?desde=2026-01-01&hasta=2026-01-31`
- **THEN** the response SHALL be an array of objects each with `fecha` (date) and `cantidad` (int) for each day in the range where actions occurred

#### Scenario: Acciones por día filtered by materia

- **WHEN** a user sends GET to `/api/auditoria/metricas/acciones-por-dia?materia_id=<uuid>`
- **THEN** the response SHALL include only counts for entries matching that materia_id

#### Scenario: Acciones por día is scoped to tenant

- **WHEN** a user from tenant A sends GET to `/api/auditoria/metricas/acciones-por-dia`
- **THEN** the response SHALL NOT include entries from tenant B

#### Scenario: Acciones por día without auditoria:ver returns 403

- **WHEN** a user WITHOUT `auditoria:ver` sends GET to `/api/auditoria/metricas/acciones-por-dia`
- **THEN** the response SHALL be `403 Forbidden`

### Requirement: Metric — Interacciones por docente

The system SHALL provide `GET /api/auditoria/metricas/por-docente` returning aggregated action counts grouped by actor (docente). The endpoint SHALL support optional query parameters: `desde` (datetime), `hasta` (datetime), `materia_id` (UUID). Each result SHALL include: `docente_id` (UUID), `docente_nombre` (string from Usuario lookup), `total` (int), and `detalle_por_accion` (dict mapping action code → count). Results SHALL be ordered by total descending. Guarded by `require_permission("auditoria:ver")` and tenant-scoped.

#### Scenario: Por docente returns grouped counts

- **WHEN** a user with `auditoria:ver` sends GET to `/api/auditoria/metricas/por-docente`
- **THEN** the response SHALL be an array of entries grouped by actor_id with total count and breakdown by action code

#### Scenario: Por docente filtered by date range

- **WHEN** a user sends GET to `/api/auditoria/metricas/por-docente?desde=2026-01-01&hasta=2026-01-31`
- **THEN** the response SHALL include only entries within that date range

#### Scenario: Por docente scoped to tenant

- **WHEN** a user from tenant A sends GET to `/api/auditoria/metricas/por-docente`
- **THEN** the response SHALL NOT include entries from tenant B

### Requirement: Metric — Interacciones por docente × materia

The system SHALL provide `GET /api/auditoria/metricas/por-materia` returning action counts grouped by `(actor_id, materia_id)`. The endpoint SHALL support optional query parameters: `desde` (datetime), `hasta` (datetime), `actor_id` (UUID). Each result SHALL include: `docente_id` (UUID), `materia_id` (UUID), `materia_nombre` (string from Materia lookup), and `total` (int). Results SHALL be ordered by total descending. Guarded by `require_permission("auditoria:ver")` and tenant-scoped.

#### Scenario: Por materia returns docente×materia counts

- **WHEN** a user with `auditoria:ver` sends GET to `/api/auditoria/metricas/por-materia`
- **THEN** the response SHALL be an array of entries grouped by actor_id and materia_id with total counts

#### Scenario: Por materia filtered by actor

- **WHEN** a user sends GET to `/api/auditoria/metricas/por-materia?actor_id=<uuid>`
- **THEN** the response SHALL include only entries for that actor

#### Scenario: Por materia scoped to tenant

- **WHEN** a user from tenant A sends GET to `/api/auditoria/metricas/por-materia`
- **THEN** the response SHALL NOT include entries from tenant B

### Requirement: Metric — Estado de comunicaciones por docente

The system SHALL provide `GET /api/auditoria/metricas/comunicaciones` returning the count of communications grouped by `(docente_id, estado)`. The endpoint SHALL support optional query parameters: `desde` (datetime), `hasta` (datetime). Each result SHALL include: `docente_id` (UUID) and `estados` (dict mapping estado string → count). Valid estados SHALL be: `Pendiente`, `En envío`, `Enviado`, `Fallido`, `Cancelado`. Guarded by `require_permission("auditoria:ver")` and tenant-scoped.

#### Scenario: Comunicaciones returns state breakdown

- **WHEN** a user with `auditoria:ver` sends GET to `/api/auditoria/metricas/comunicaciones`
- **THEN** the response SHALL be an array of entries each with `docente_id` and `estados` dict mapping estado to count

#### Scenario: Comunicaciones filtered by date range

- **WHEN** a user sends GET to `/api/auditoria/metricas/comunicaciones?desde=2026-01-01&hasta=2026-01-31`
- **THEN** the response SHALL include only communications created within that date range

#### Scenario: Comunicaciones scoped to tenant

- **WHEN** a user from tenant A sends GET to `/api/auditoria/metricas/comunicaciones`
- **THEN** the response SHALL NOT include communications from tenant B

### Requirement: Últimas N acciones

The system SHALL provide `GET /api/auditoria/ultimas-acciones` returning the last N audit log entries. The endpoint SHALL support query parameters: `limit` (integer, default 200, max 500), `offset` (integer, default 0). All optional filter parameters from the existing `/api/audit/log` SHALL also be supported: `accion`, `actor_id`, `materia_id`, `desde`, `hasta`. The endpoint SHALL be guarded by `require_permission("auditoria:ver")` and tenant-scoped. Response format SHALL match `AuditLogListResponse`.

#### Scenario: Últimas acciones returns 200 entries by default

- **WHEN** a user with `auditoria:ver` sends GET to `/api/auditoria/ultimas-acciones`
- **THEN** the response SHALL contain at most 200 entries

#### Scenario: Últimas acciones accepts custom limit

- **WHEN** a user sends GET to `/api/auditoria/ultimas-acciones?limit=50`
- **THEN** the response SHALL contain at most 50 entries

#### Scenario: Últimas acciones rejects limit above 500

- **WHEN** a user sends GET to `/api/auditoria/ultimas-acciones?limit=1000`
- **THEN** the response SHALL be a 422 validation error

#### Scenario: Últimas acciones applies filters

- **WHEN** a user sends GET to `/api/auditoria/ultimas-acciones?accion=CALIFICACIONES_IMPORTAR`
- **THEN** the response SHALL include only entries with that exact action code
