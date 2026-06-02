## 1. Migration

- [x] 1.1 Create Alembic migration 007 with `calificacion` and `umbral_materia` tables
- [x] 1.2 Add `calificaciones:configurar-umbral` permission to PROFESOR, COORDINADOR and ADMIN roles in migration

## 2. Models

- [x] 2.1 Create `backend/app/models/calificacion.py`
- [x] 2.2 Create `backend/app/models/umbral_materia.py`
- [x] 2.3 Register both models in `backend/app/models/__init__.py`

## 3. Schemas

- [x] 3.1 Create `backend/app/schemas/calificacion.py` with request/response schemas
- [x] 3.2 Create `backend/app/schemas/umbral_materia.py` with request/response schemas

## 4. Repositories

- [x] 4.1 Create `backend/app/repositories/calificacion_repository.py`
- [x] 4.2 Create `backend/app/repositories/umbral_materia_repository.py`

## 5. Service

- [x] 5.1 Create `backend/app/services/calificacion_service.py` with import preview, import confirm, list, aprobado derivation logic

## 6. Router

- [x] 6.1 Create `backend/app/api/v1/routers/calificaciones.py` with preview, confirm, list, umbral GET and PUT endpoints
- [x] 6.2 Register the router in `backend/app/main.py`

## 7. Seed Permissions

- [x] 7.1 Add `calificaciones:configurar-umbral` to seed_auth.py SYSTEM_ROLES

## 8. Tests

- [x] 8.1 Write unit tests for `aprobado` derivation (numeric >= threshold, textual in approved set)
- [x] 8.2 Write integration test for import preview with column detection
- [x] 8.3 Write integration test for confirm import creates records
- [x] 8.4 Write integration test for umbral config per materia (doesn't affect others)
- [x] 8.5 Write integration test for permission guards

## 9. Docs

- [x] 9.1 Mark C-10 as completed in CHANGES.md
