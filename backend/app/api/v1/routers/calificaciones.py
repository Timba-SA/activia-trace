import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user, require_permission
from app.repositories.umbral_materia_repository import UmbralMateriaRepository
from app.schemas.auth import CurrentUser
from app.schemas.calificacion import (
    CalificacionListResponse,
    CalificacionResponse,
    ImportConfirmRequest,
    ImportConfirmResponse,
    ImportPreviewResponse,
)
from app.schemas.umbral_materia import (
    UmbralMateriaDefaultResponse,
    UmbralMateriaResponse,
    UmbralMateriaUpdate,
)
from app.services.calificacion_service import CalificacionService

router = APIRouter(prefix="/api/v1", tags=["calificaciones"])


@router.post("/calificaciones/import/preview", response_model=ImportPreviewResponse)
async def preview_import(
    materia_id: uuid.UUID = Query(...),
    cohorte_id: uuid.UUID = Query(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("calificaciones:importar")),
):
    content = await file.read()
    service = CalificacionService(db, current_user.tenant_id, current_user.id)
    result = await service.preview_import(materia_id, cohorte_id, content)
    return ImportPreviewResponse(**result)


@router.post("/calificaciones/import/confirm", response_model=ImportConfirmResponse, status_code=status.HTTP_201_CREATED)
async def confirm_import(
    body: ImportConfirmRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("calificaciones:importar")),
):
    service = CalificacionService(db, current_user.tenant_id, current_user.id)
    result = await service.confirm_import(
        materia_id=body.materia_id,
        cohorte_id=body.cohorte_id,
        selected_activities=body.selected_activities,
        preview_hash=body.preview_hash,
        rows=[r.model_dump() for r in body.rows],
    )
    return ImportConfirmResponse(**result)


@router.get("/calificaciones", response_model=CalificacionListResponse)
async def list_calificaciones(
    materia_id: uuid.UUID = Query(...),
    cohorte_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("calificaciones:importar")),
):
    service = CalificacionService(db, current_user.tenant_id, current_user.id)
    items, total, pages = await service.list_calificaciones(materia_id, cohorte_id)
    return CalificacionListResponse(
        items=[CalificacionResponse.model_validate(c) for c in items],
        total=total,
        pages=pages,
    )


@router.get("/umbrales", response_model=UmbralMateriaResponse | UmbralMateriaDefaultResponse)
async def get_umbral(
    materia_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    repo = UmbralMateriaRepository(db, current_user.tenant_id)
    umbral = await repo.get_by_materia(materia_id)
    if umbral is None:
        return UmbralMateriaDefaultResponse(materia_id=materia_id)
    return UmbralMateriaResponse.model_validate(umbral)


@router.put("/umbrales/{id}", response_model=UmbralMateriaResponse)
async def update_umbral(
    id: uuid.UUID,
    body: UmbralMateriaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("calificaciones:configurar-umbral")),
):
    repo = UmbralMateriaRepository(db, current_user.tenant_id)
    umbral = await repo.update(
        id,
        umbral_pct=body.umbral_pct,
        valores_aprobados=body.valores_aprobados,
    )
    return UmbralMateriaResponse.model_validate(umbral)


@router.put("/umbrales/materia/{materia_id}", response_model=UmbralMateriaResponse)
async def upsert_umbral_by_materia(
    materia_id: uuid.UUID,
    body: UmbralMateriaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("calificaciones:configurar-umbral")),
):
    repo = UmbralMateriaRepository(db, current_user.tenant_id)
    umbral = await repo.upsert(
        materia_id=materia_id,
        tenant_id=current_user.tenant_id,
        umbral_pct=body.umbral_pct,
        valores_aprobados=body.valores_aprobados,
    )
    return UmbralMateriaResponse.model_validate(umbral)
