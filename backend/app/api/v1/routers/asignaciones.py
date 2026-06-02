import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.asignacion import (
    AsignacionCreate,
    AsignacionListResponse,
    AsignacionResponse,
    AsignacionUpdate,
)
from app.schemas.auth import CurrentUser
from app.services.asignacion_service import AsignacionService

router = APIRouter(prefix="/api/admin/asignaciones", tags=["asignaciones"])


@router.get("", response_model=AsignacionListResponse)
async def list_asignaciones(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("usuarios:asignar")),
):
    service = AsignacionService(db, current_user.tenant_id)
    items, total, pages = await service.list(limit=limit, offset=offset)
    return AsignacionListResponse(
        items=[AsignacionResponse.model_validate(r) for r in items],
        total=total,
        pages=pages,
    )


@router.post("", response_model=AsignacionResponse, status_code=status.HTTP_201_CREATED)
async def create_asignacion(
    body: AsignacionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("usuarios:asignar")),
):
    service = AsignacionService(db, current_user.tenant_id)
    asignacion = await service.create(body)
    return AsignacionResponse.model_validate(asignacion)


@router.get("/{asignacion_id}", response_model=AsignacionResponse)
async def get_asignacion(
    asignacion_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("usuarios:asignar")),
):
    service = AsignacionService(db, current_user.tenant_id)
    asignacion = await service.get(asignacion_id)
    return AsignacionResponse.model_validate(asignacion)


@router.put("/{asignacion_id}", response_model=AsignacionResponse)
async def update_asignacion(
    asignacion_id: uuid.UUID,
    body: AsignacionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("usuarios:asignar")),
):
    service = AsignacionService(db, current_user.tenant_id)
    asignacion = await service.update(asignacion_id, body)
    return AsignacionResponse.model_validate(asignacion)


@router.delete("/{asignacion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asignacion(
    asignacion_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("usuarios:asignar")),
):
    service = AsignacionService(db, current_user.tenant_id)
    await service.soft_delete(asignacion_id)
