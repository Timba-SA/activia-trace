import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.auth import CurrentUser
from app.schemas.factura import (
    FacturaCreate,
    FacturaEstadoUpdate,
    FacturaListResponse,
    FacturaResponse,
)
from app.services.factura_service import FacturaService

router = APIRouter(prefix="/api/facturas", tags=["facturas"])


@router.post("", response_model=FacturaResponse, status_code=status.HTTP_201_CREATED)
async def create_factura(
    body: FacturaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("liquidaciones:gestionar-facturas")),
):
    service = FacturaService(db, current_user.tenant_id)
    return await service.crear(body)


@router.get("", response_model=FacturaListResponse)
async def list_facturas(
    periodo: str | None = None,
    usuario_id: uuid.UUID | None = None,
    estado: str | None = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("liquidaciones:ver")),
):
    service = FacturaService(db, current_user.tenant_id)
    items, total = await service.listar(
        periodo=periodo,
        usuario_id=usuario_id,
        estado=estado,
        limit=limit,
        offset=offset,
    )
    page = (offset // limit) + 1
    return FacturaListResponse(items=items, total=total, page=page, page_size=limit)


@router.patch("/{factura_id}/estado", response_model=FacturaResponse)
async def cambiar_estado_factura(
    factura_id: uuid.UUID,
    body: FacturaEstadoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("liquidaciones:gestionar-facturas")),
):
    service = FacturaService(db, current_user.tenant_id)
    return await service.cambiar_estado(factura_id, body)
