import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import CurrentUser
from app.schemas.aviso import (
    AckResponse,
    AvisoCreate,
    AvisoListResponse,
    AvisoResponse,
    AvisoStatsResponse,
    AvisoUpdate,
)
from app.services.aviso_service import AvisosService

router = APIRouter(prefix="/api/avisos", tags=["avisos"])


@router.get("/", response_model=AvisoListResponse)
async def listar_avisos(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("avisos:publicar")),
):
    service = AvisosService(db, current_user.tenant_id, current_user.id)
    items, total = await service.listar_avisos(limit=limit, offset=offset)
    return AvisoListResponse(
        items=items, total=total, page=offset // limit + 1, page_size=limit
    )


@router.post("/", response_model=AvisoResponse, status_code=status.HTTP_201_CREATED)
async def crear_aviso(
    body: AvisoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("avisos:publicar")),
):
    service = AvisosService(db, current_user.tenant_id, current_user.id)
    return await service.crear_aviso(body)


@router.get("/mis-avisos", response_model=AvisoListResponse)
async def listar_mis_avisos(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    service = AvisosService(db, current_user.tenant_id, current_user.id)
    items, total = await service.listar_mis_avisos(limit=limit, offset=offset)
    return AvisoListResponse(
        items=items, total=total, page=offset // limit + 1, page_size=limit
    )


@router.get("/{id}", response_model=AvisoResponse)
async def obtener_aviso(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("avisos:publicar")),
):
    service = AvisosService(db, current_user.tenant_id, current_user.id)
    return await service.obtener_aviso(id)


@router.patch("/{id}", response_model=AvisoResponse)
async def actualizar_aviso(
    id: uuid.UUID,
    body: AvisoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("avisos:publicar")),
):
    service = AvisosService(db, current_user.tenant_id, current_user.id)
    return await service.actualizar_aviso(id, body)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_aviso(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("avisos:publicar")),
):
    service = AvisosService(db, current_user.tenant_id, current_user.id)
    await service.eliminar_aviso(id)


@router.post("/{id}/ack", response_model=AckResponse)
async def confirmar_lectura(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    service = AvisosService(db, current_user.tenant_id, current_user.id)
    return await service.confirmar_lectura(id, current_user.id)


@router.get("/{id}/stats", response_model=AvisoStatsResponse)
async def obtener_stats(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("avisos:publicar")),
):
    service = AvisosService(db, current_user.tenant_id, current_user.id)
    return await service.obtener_stats(id)
