import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.auth import CurrentUser
from app.schemas.cohorte import (
    CohorteCreate,
    CohorteListResponse,
    CohorteResponse,
    CohorteUpdate,
)
from app.services.estructura_service import CohorteService

router = APIRouter(prefix="/api/admin/cohortes", tags=["cohortes"])


@router.get("", response_model=CohorteListResponse)
async def list_cohortes(
    limit: int = 20,
    offset: int = 0,
    carrera_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
):
    service = CohorteService(db, current_user.tenant_id)
    items, total, pages = await service.list(
        limit=limit, offset=offset, carrera_id=carrera_id,
    )
    return CohorteListResponse(
        items=[CohorteResponse.model_validate(r) for r in items],
        total=total,
        pages=pages,
    )


@router.get("/{cohorte_id}", response_model=CohorteResponse)
async def get_cohorte(
    cohorte_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
):
    service = CohorteService(db, current_user.tenant_id)
    cohorte = await service.get(cohorte_id)
    return CohorteResponse.model_validate(cohorte)


@router.post("", response_model=CohorteResponse, status_code=status.HTTP_201_CREATED)
async def create_cohorte(
    body: CohorteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
):
    service = CohorteService(db, current_user.tenant_id)
    cohorte = await service.create(body)
    return CohorteResponse.model_validate(cohorte)


@router.put("/{cohorte_id}", response_model=CohorteResponse)
async def update_cohorte(
    cohorte_id: uuid.UUID,
    body: CohorteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
):
    service = CohorteService(db, current_user.tenant_id)
    cohorte = await service.update(cohorte_id, body)
    return CohorteResponse.model_validate(cohorte)


@router.delete("/{cohorte_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cohorte(
    cohorte_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
):
    service = CohorteService(db, current_user.tenant_id)
    await service.soft_delete(cohorte_id)
