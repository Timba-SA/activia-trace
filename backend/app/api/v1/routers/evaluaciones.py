import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.auth import CurrentUser
from app.schemas.coloquio import (
    ConvocatoriaAlumnoImport,
    EvaluacionCreate,
    EvaluacionListResponse,
    EvaluacionResponse,
    EvaluacionUpdate,
)
from app.services.coloquio_service import ColoquioService

router = APIRouter(prefix="/api/coloquios", tags=["coloquios"])


@router.post("/convocatorias", response_model=EvaluacionResponse, status_code=status.HTTP_201_CREATED)
async def crear_convocatoria(
    body: EvaluacionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("coloquios:gestionar")),
):
    service = ColoquioService(db, current_user.tenant_id, current_user.id)
    return await service.crear_convocatoria(body)


@router.get("/convocatorias", response_model=EvaluacionListResponse)
async def listar_convocatorias(
    materia_id: uuid.UUID | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("coloquios:ver")),
):
    service = ColoquioService(db, current_user.tenant_id, current_user.id)
    items, total, pages = await service.listar_convocatorias(
        materia_id=materia_id,
        limit=limit,
        offset=offset,
    )
    return EvaluacionListResponse(items=items, total=total, pages=pages)


@router.get("/convocatorias/{id}", response_model=EvaluacionResponse)
async def obtener_convocatoria(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("coloquios:ver")),
):
    service = ColoquioService(db, current_user.tenant_id, current_user.id)
    items, _, _ = await service.listar_convocatorias(limit=1, offset=0)
    for item in items:
        if item.id == id:
            return item
    from fastapi import HTTPException
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Convocatoria no encontrada")


@router.patch("/convocatorias/{id}", response_model=EvaluacionResponse)
async def actualizar_convocatoria(
    id: uuid.UUID,
    body: EvaluacionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("coloquios:gestionar")),
):
    service = ColoquioService(db, current_user.tenant_id, current_user.id)
    return await service.actualizar_convocatoria(id, body)


@router.post("/convocatorias/{id}/importar-alumnos")
async def importar_alumnos(
    id: uuid.UUID,
    body: ConvocatoriaAlumnoImport,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("coloquios:gestionar")),
):
    service = ColoquioService(db, current_user.tenant_id, current_user.id)
    return await service.importar_padron(id, body.alumno_ids)


@router.post("/convocatorias/{id}/cerrar", status_code=status.HTTP_204_NO_CONTENT)
async def cerrar_convocatoria(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("coloquios:gestionar")),
):
    service = ColoquioService(db, current_user.tenant_id, current_user.id)
    await service.cerrar_convocatoria(id)
