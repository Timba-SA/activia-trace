import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.auth import CurrentUser
from app.schemas.fecha_academica import (
    FechaAcademicaCreate,
    FechaAcademicaListResponse,
    FechaAcademicaResponse,
    FechaAcademicaUpdate,
)
from app.services.fecha_academica_service import FechaAcademicaService

router = APIRouter(prefix="/api/fechas-academicas", tags=["fechas-academicas"])


@router.get("/", response_model=FechaAcademicaListResponse)
async def list_fechas(
    materia_id: uuid.UUID | None = Query(None),
    cohorte_id: uuid.UUID | None = Query(None),
    tipo: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("programas:ver")),
):
    service = FechaAcademicaService(db, current_user.tenant_id, current_user.id)
    filters = {}
    if materia_id:
        filters["materia_id"] = materia_id
    if cohorte_id:
        filters["cohorte_id"] = cohorte_id
    if tipo:
        filters["tipo"] = tipo
    items, total, pages = await service.list(filters, limit=limit, offset=offset)
    return FechaAcademicaListResponse(
        items=items, total=total, page=offset // limit + 1, page_size=limit
    )


@router.post("/", response_model=FechaAcademicaResponse, status_code=status.HTTP_201_CREATED)
async def create_fecha(
    body: FechaAcademicaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("programas:gestionar")),
):
    service = FechaAcademicaService(db, current_user.tenant_id, current_user.id)
    return await service.create(body)


@router.get("/{id}", response_model=FechaAcademicaResponse)
async def get_fecha(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("programas:ver")),
):
    service = FechaAcademicaService(db, current_user.tenant_id, current_user.id)
    return await service.get_by_id(id)


@router.patch("/{id}", response_model=FechaAcademicaResponse)
async def update_fecha(
    id: uuid.UUID,
    body: FechaAcademicaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("programas:gestionar")),
):
    service = FechaAcademicaService(db, current_user.tenant_id, current_user.id)
    return await service.update(id, body)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fecha(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("programas:gestionar")),
):
    service = FechaAcademicaService(db, current_user.tenant_id, current_user.id)
    await service.delete(id)
