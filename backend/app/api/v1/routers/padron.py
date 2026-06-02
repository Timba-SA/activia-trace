import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user, require_permission
from app.schemas.auth import CurrentUser
from app.schemas.padron import (
    EntradaPadronListResponse,
    EntradaPadronResponse,
    PadronConfirmRequest,
    PadronConfirmResponse,
    PadronPreviewResponse,
    VersionPadronListResponse,
    VersionPadronResponse,
)
from app.services.padron_service import PadronService

router = APIRouter(prefix="/api/v1/padron", tags=["padron"])


@router.post("/upload", response_model=PadronPreviewResponse)
async def preview_upload(
    materia_id: uuid.UUID = Query(...),
    cohorte_id: uuid.UUID = Query(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("padron:cargar")),
):
    content = await file.read()
    service = PadronService(db, current_user.tenant_id, current_user.id)
    result = await service.preview_upload(materia_id, cohorte_id, content)
    return PadronPreviewResponse(**result)


@router.post("/confirm", response_model=PadronConfirmResponse, status_code=status.HTTP_201_CREATED)
async def confirm_upload(
    body: PadronConfirmRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("padron:cargar")),
):
    service = PadronService(db, current_user.tenant_id, current_user.id)
    result = await service.confirm_upload(
        materia_id=body.materia_id,
        cohorte_id=body.cohorte_id,
        preview_hash=body.preview_hash,
        entries=[e.model_dump() for e in body.entries],
    )
    return PadronConfirmResponse(**result)


@router.get("/activo", response_model=VersionPadronResponse)
async def get_active_padron(
    materia_id: uuid.UUID = Query(...),
    cohorte_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("padron:cargar")),
):
    service = PadronService(db, current_user.tenant_id, current_user.id)
    version = await service.get_active_padron(materia_id, cohorte_id)
    if version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active padron version found for this materia and cohorte",
        )
    return VersionPadronResponse.model_validate(version)


@router.get("/versiones", response_model=VersionPadronListResponse)
async def list_versiones(
    materia_id: uuid.UUID = Query(...),
    cohorte_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("padron:cargar")),
):
    service = PadronService(db, current_user.tenant_id, current_user.id)
    items, total, pages = await service.get_versiones(materia_id, cohorte_id)
    return VersionPadronListResponse(
        items=[VersionPadronResponse.model_validate(v) for v in items],
        total=total,
        pages=pages,
    )


@router.get("/versiones/{version_id}/entradas", response_model=EntradaPadronListResponse)
async def list_entradas(
    version_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("padron:cargar")),
):
    service = PadronService(db, current_user.tenant_id, current_user.id)
    items, total, pages = await service.get_entradas(version_id)
    return EntradaPadronListResponse(
        items=[EntradaPadronResponse.model_validate(e) for e in items],
        total=total,
        pages=pages,
    )
