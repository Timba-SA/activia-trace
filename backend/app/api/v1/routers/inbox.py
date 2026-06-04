import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.schemas.auth import CurrentUser
from app.schemas.mensaje import MensajeCreate, MensajeListResponse, MensajeOut, MensajeResponder
from app.services.mensajeria_service import MensajeriaService

router = APIRouter(prefix="/api/inbox", tags=["inbox"])


@router.get("", response_model=MensajeListResponse)
async def list_inbox(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    offset = (page - 1) * page_size
    service = MensajeriaService(db, current_user.tenant_id, current_user.id)
    items, total = await service.list_inbox(limit=page_size, offset=offset)
    return MensajeListResponse(
        items=[MensajeOut.model_validate(m) for m in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{mensaje_id}", response_model=MensajeOut)
async def get_mensaje(
    mensaje_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    service = MensajeriaService(db, current_user.tenant_id, current_user.id)
    try:
        return await service.get_mensaje(mensaje_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mensaje no encontrado",
        )


@router.post("", response_model=MensajeOut, status_code=status.HTTP_201_CREATED)
async def enviar_mensaje(
    body: MensajeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    service = MensajeriaService(db, current_user.tenant_id, current_user.id)
    return await service.enviar_mensaje(body)


@router.post("/{mensaje_id}/responder", response_model=MensajeOut, status_code=status.HTTP_201_CREATED)
async def responder_mensaje(
    mensaje_id: uuid.UUID,
    body: MensajeResponder,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    service = MensajeriaService(db, current_user.tenant_id, current_user.id)
    return await service.responder_mensaje(mensaje_id, body)
