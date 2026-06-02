## 1. Migration

- [ ] 1.1 Create Alembic migration 006 with version_padron and entrada_padron tables, FK constraints, and indexes
- [ ] 1.2 Add permission `padron:cargar` to ADMIN and COORDINADOR roles in migration 006

## 2. Models

- [ ] 2.1 Create `VersionPadron` model with BaseModelMixin
- [ ] 2.2 Create `EntradaPadron` model with BaseModelMixin
- [ ] 2.3 Export both models in `models/__init__.py`

## 3. Schemas

- [ ] 3.1 Create Pydantic schemas: VersionPadronCreate/Response, EntradaPadronResponse, PadronUploadResponse, PadronPreviewResponse, PadronConfirmRequest
- [ ] 3.2 Add `ConfigDict(extra='forbid')` and `from_attributes=True` where appropriate

## 4. Repositories

- [ ] 4.1 Create `VersionPadronRepository` with `get_active`, `get_active_for_materia_cohorte`, `deactivate_all_for_materia_cohorte`
- [ ] 4.2 Create `EntradaPadronRepository` with `bulk_create`, `list_by_version`

## 5. Service

- [ ] 5.1 Create `PadronService` with methods: `preview_upload`, `confirm_upload`, `get_active_padron`, `get_versiones`, `get_entradas`

## 6. Router

- [ ] 6.1 Create `padron.py` router with endpoints: POST /api/v1/padron/upload, POST /api/v1/padron/confirm, GET /api/v1/padron/activo, GET /api/v1/padron/versiones, GET /api/v1/padron/versiones/{id}/entradas
- [ ] 6.2 Guard all endpoints with `require_permission("padron:cargar")`
- [ ] 6.3 Register router in main.py

## 7. Moodle WS Client

- [ ] 7.1 Create `integrations/moodle_ws.py` with async MoodleWSClient class

## 8. Seed

- [ ] 8.1 Add `padron:cargar` to ADMIN and COORDINADOR permissions in `scripts/seed_auth.py`

## 9. Tests

- [ ] 9.1 Write test for upload preview flow
- [ ] 9.2 Write test for confirm creates version + deactivates previous
- [ ] 9.3 Write test for entrada without usuario_id
- [ ] 9.4 Write test for tenant isolation
- [ ] 9.5 Write test for permission guard (403 without padron:cargar)
- [ ] 9.6 Write test for MoodleWSClient instantiation
