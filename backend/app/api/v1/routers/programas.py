import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.auth import CurrentUser
from app.schemas.programa_materia import (
    GenerarContenidoResponse,
    ProgramaMateriaCreate,
    ProgramaMateriaListResponse,
    ProgramaMateriaResponse,
    ProgramaMateriaUpdate,
)
from app.services.programa_materia_service import ProgramaMateriaService

router = APIRouter(prefix="/api/programas", tags=["programas"])


@router.get("/", response_model=ProgramaMateriaListResponse)
async def list_programas(
    materia_id: uuid.UUID | None = Query(None),
    carrera_id: uuid.UUID | None = Query(None),
    cohorte_id: uuid.UUID | None = Query(None),
    activo: bool | None = Query(None),
    incluir_inactivos: bool = Query(False),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("programas:ver")),
):
    service = ProgramaMateriaService(db, current_user.tenant_id, current_user.id)
    filters = {}
    if materia_id:
        filters["materia_id"] = materia_id
    if carrera_id:
        filters["carrera_id"] = carrera_id
    if cohorte_id:
        filters["cohorte_id"] = cohorte_id
    if activo is not None:
        filters["activo"] = activo
    if incluir_inactivos:
        filters["incluir_inactivos"] = incluir_inactivos
    items, total, pages = await service.list(filters, limit=limit, offset=offset)
    return ProgramaMateriaListResponse(
        items=items, total=total, page=offset // limit + 1, page_size=limit
    )


@router.post("/", response_model=ProgramaMateriaResponse, status_code=status.HTTP_201_CREATED)
async def create_programa(
    body: ProgramaMateriaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("programas:gestionar")),
):
    service = ProgramaMateriaService(db, current_user.tenant_id, current_user.id)
    return await service.create(body)


@router.get("/{id}", response_model=ProgramaMateriaResponse)
async def get_programa(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("programas:ver")),
):
    service = ProgramaMateriaService(db, current_user.tenant_id, current_user.id)
    return await service.get_by_id(id)


@router.patch("/{id}", response_model=ProgramaMateriaResponse)
async def update_programa(
    id: uuid.UUID,
    body: ProgramaMateriaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("programas:gestionar")),
):
    service = ProgramaMateriaService(db, current_user.tenant_id, current_user.id)
    return await service.update(id, body)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_programa(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("programas:gestionar")),
):
    service = ProgramaMateriaService(db, current_user.tenant_id, current_user.id)
    await service.deactivate(id)


@router.post("/{id}/generar-contenido", response_model=GenerarContenidoResponse)
async def generar_contenido(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("programas:gestionar")),
):
    service = ProgramaMateriaService(db, current_user.tenant_id, current_user.id)
    return await service.generar_contenido(id)
