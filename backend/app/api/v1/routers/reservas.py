import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.auth import CurrentUser
from app.schemas.coloquio import ReservaCancelResponse, ReservaCreate, ReservaResponse
from app.services.coloquio_service import ColoquioService

router = APIRouter(prefix="/api/coloquios/reservas", tags=["coloquios"])


@router.post("", response_model=ReservaResponse, status_code=status.HTTP_201_CREATED)
async def reservar_turno(
    evaluacion_id: uuid.UUID,
    body: ReservaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("coloquios:reservar")),
):
    service = ColoquioService(db, current_user.tenant_id, current_user.id)
    return await service.reservar_turno(evaluacion_id, body.turno_id, current_user.id)


@router.patch("/{id}/cancelar", response_model=ReservaCancelResponse)
async def cancelar_reserva(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("coloquios:reservar")),
):
    service = ColoquioService(db, current_user.tenant_id, current_user.id)
    await service.cancelar_reserva(id)
    return ReservaCancelResponse(message="Reserva cancelada exitosamente")
