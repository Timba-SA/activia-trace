## Why

The system already records every significant action in the immutable audit log (C-05), but there is no way to visualize patterns, monitor volume trends, or drill into communication states across docents. ADMIN and COORDINADOR need a metrics dashboard to detect anomalies, track system usage, and audit behaviors without raw SQL access.

## What Changes

- Add **5 new endpoints** under `/api/auditoria/` for aggregated metrics and the complete log view
- Implement metric aggregation queries on the existing `audit_log` table (no schema changes)
- Expose `GET /api/auditoria/ultimas-acciones` as a convenience wrapper (last N, default 200)
- Register `auditoria:ver` in the existing RBAC permission catalog if not already present (ADMIN, COORDINADOR scope propio, FINANZAS)
- No migration needed — all queries are read-only against the existing `audit_log` table

## Capabilities

### New Capabilities

- `auditoria-metricas`: Aggregate audit metrics — acciones-por-dia, por-docente, por-materia, and communication state breakdown. All read-only, tenant-scoped, guarded by `auditoria:ver`.

### Modified Capabilities

- `audit-log-model`: Add scenarios for `GET /api/auditoria/ultimas-acciones` (last N convenience endpoint) and the extended metric endpoints. The existing `/api/audit/log` list endpoint is already defined; this change adds the dashboard layer on top.

## Impact

- Backend: new routes at `routers/auditoria.py` (or extend existing `routers/audit.py`), new service methods for aggregations, new repository query methods on `AuditLogRepository`
- No migration, no new tables, no model changes
- RBAC: ensure `auditoria:ver` permission exists (already in knowledge-base matrix, may need seed if not yet in code)
- Frontend: no changes in this change (future UI work is separate)
