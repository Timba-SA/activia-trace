import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.auth import CurrentUser
from app.schemas.comunicacion import (
    AprobarResponse,
    CancelarResponse,
    EnvioRequest,
    EnvioResponse,
    EstadoResponse,
    PreviewRequest,
    PreviewResponse,
)
from app.services.comunicacion_service import ComunicacionService

router = APIRouter(prefix="/api/v1", tags=["comunicaciones"])


@router.post("/comunicaciones/preview", response_model=PreviewResponse)
async def preview_comunicacion(
    body: PreviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("comunicacion:enviar")),
):
    service = ComunicacionService(db, current_user.tenant_id, current_user.id)
    result = await service.preview(
        materia_id=body.materia_id,
        cohorte_id=body.cohorte_id,
        destinatario_entrada_ids=body.destinatario_entrada_ids,
        asunto_template=body.asunto_template,
        cuerpo_template=body.cuerpo_template,
    )
    return result


@router.post(
    "/comunicaciones/enviar",
    response_model=EnvioResponse,
    status_code=status.HTTP_201_CREATED,
)
async def enviar_comunicacion(
    body: EnvioRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("comunicacion:enviar")),
):
    service = ComunicacionService(db, current_user.tenant_id, current_user.id)
    result = await service.enviar(
        materia_id=body.materia_id,
        cohorte_id=body.cohorte_id,
        destinatario_entrada_ids=body.destinatario_entrada_ids,
        asunto=body.asunto,
        cuerpo=body.cuerpo,
    )
    return result


@router.get("/comunicaciones/estado", response_model=EstadoResponse)
async def estado_comunicacion(
    lote_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("comunicacion:enviar")),
):
    service = ComunicacionService(db, current_user.tenant_id, current_user.id)
    result = await service.get_estado(lote_id)
    return result


@router.post(
    "/comunicaciones/lote/{lote_id}/aprobar",
    response_model=AprobarResponse,
)
async def aprobar_lote(
    lote_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("comunicacion:aprobar")),
):
    service = ComunicacionService(db, current_user.tenant_id, current_user.id)
    result = await service.aprobar_lote(lote_id)
    return result


@router.post(
    "/comunicaciones/lote/{lote_id}/cancelar",
    response_model=CancelarResponse,
)
async def cancelar_lote(
    lote_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("comunicacion:aprobar")),
):
    service = ComunicacionService(db, current_user.tenant_id, current_user.id)
    result = await service.cancelar_lote(lote_id)
    return result
