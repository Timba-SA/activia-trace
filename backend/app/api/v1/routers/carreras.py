import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.auth import CurrentUser
from app.schemas.carrera import (
    CarreraCreate,
    CarreraListResponse,
    CarreraResponse,
    CarreraUpdate,
)
from app.services.estructura_service import CarreraService

router = APIRouter(prefix="/api/admin/carreras", tags=["carreras"])


@router.get("", response_model=CarreraListResponse)
async def list_carreras(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
):
    service = CarreraService(db, current_user.tenant_id)
    items, total, pages = await service.list(limit=limit, offset=offset)
    return CarreraListResponse(
        items=[CarreraResponse.model_validate(r) for r in items],
        total=total,
        pages=pages,
    )


@router.get("/{carrera_id}", response_model=CarreraResponse)
async def get_carrera(
    carrera_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
):
    service = CarreraService(db, current_user.tenant_id)
    carrera = await service.get(carrera_id)
    return CarreraResponse.model_validate(carrera)


@router.post("", response_model=CarreraResponse, status_code=status.HTTP_201_CREATED)
async def create_carrera(
    body: CarreraCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
):
    service = CarreraService(db, current_user.tenant_id)
    carrera = await service.create(body)
    return CarreraResponse.model_validate(carrera)


@router.put("/{carrera_id}", response_model=CarreraResponse)
async def update_carrera(
    carrera_id: uuid.UUID,
    body: CarreraUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
):
    service = CarreraService(db, current_user.tenant_id)
    carrera = await service.update(carrera_id, body)
    return CarreraResponse.model_validate(carrera)


@router.delete("/{carrera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_carrera(
    carrera_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
):
    service = CarreraService(db, current_user.tenant_id)
    await service.soft_delete(carrera_id)
