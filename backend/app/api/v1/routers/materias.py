import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.auth import CurrentUser
from app.schemas.materia import (
    MateriaCreate,
    MateriaListResponse,
    MateriaResponse,
    MateriaUpdate,
)
from app.services.estructura_service import MateriaService

router = APIRouter(prefix="/api/admin/materias", tags=["materias"])


@router.get("", response_model=MateriaListResponse)
async def list_materias(
    limit: int = 20,
    offset: int = 0,
    carrera_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
):
    service = MateriaService(db, current_user.tenant_id)
    items, total, pages = await service.list(
        limit=limit, offset=offset, carrera_id=carrera_id,
    )
    return MateriaListResponse(
        items=[MateriaResponse.model_validate(r) for r in items],
        total=total,
        pages=pages,
    )


@router.get("/{materia_id}", response_model=MateriaResponse)
async def get_materia(
    materia_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
):
    service = MateriaService(db, current_user.tenant_id)
    materia = await service.get(materia_id)
    return MateriaResponse.model_validate(materia)


@router.post("", response_model=MateriaResponse, status_code=status.HTTP_201_CREATED)
async def create_materia(
    body: MateriaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
):
    service = MateriaService(db, current_user.tenant_id)
    materia = await service.create(body)
    return MateriaResponse.model_validate(materia)


@router.put("/{materia_id}", response_model=MateriaResponse)
async def update_materia(
    materia_id: uuid.UUID,
    body: MateriaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
):
    service = MateriaService(db, current_user.tenant_id)
    materia = await service.update(materia_id, body)
    return MateriaResponse.model_validate(materia)


@router.delete("/{materia_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_materia(
    materia_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
):
    service = MateriaService(db, current_user.tenant_id)
    await service.soft_delete(materia_id)
