import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.models.guardia import EstadoGuardia
from app.schemas.auth import CurrentUser
from app.schemas.guardia import (
    GuardiaCreate,
    GuardiaListResponse,
    GuardiaResponse,
    GuardiaUpdate,
)
from app.services.guardia_service import GuardiaService

router = APIRouter(prefix="/api/guardias", tags=["guardias"])


@router.post("", response_model=GuardiaResponse, status_code=status.HTTP_201_CREATED)
async def crear_guardia(
    body: GuardiaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("guardias:registrar")),
):
    service = GuardiaService(db, current_user.tenant_id)
    return await service.create(body)


@router.patch("/{id}", response_model=GuardiaResponse)
async def actualizar_estado_guardia(
    id: uuid.UUID,
    body: GuardiaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("guardias:registrar")),
):
    service = GuardiaService(db, current_user.tenant_id)
    return await service.update_estado(id, body.estado)


@router.get("/mis-guardias", response_model=GuardiaListResponse)
async def mis_guardias(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("guardias:registrar")),
):
    service = GuardiaService(db, current_user.tenant_id)
    items, total, pages = await service.list_mis_guardias(
        usuario_id=current_user.id,
        limit=limit,
        offset=offset,
    )
    return GuardiaListResponse(
        items=[GuardiaResponse.model_validate(g) for g in items],
        total=total,
        pages=pages,
    )


@router.get("", response_model=GuardiaListResponse)
async def listar_guardias_admin(
    materia_id: uuid.UUID | None = Query(None),
    carrera_id: uuid.UUID | None = Query(None),
    cohorte_id: uuid.UUID | None = Query(None),
    asignacion_id: uuid.UUID | None = Query(None),
    estado: EstadoGuardia | None = Query(None),
    fecha_desde: date | None = Query(None),
    fecha_hasta: date | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("guardias:ver")),
):
    service = GuardiaService(db, current_user.tenant_id)
    items, total, pages = await service.list_guardias_admin(
        materia_id=materia_id,
        carrera_id=carrera_id,
        cohorte_id=cohorte_id,
        asignacion_id=asignacion_id,
        estado=estado,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        limit=limit,
        offset=offset,
    )
    return GuardiaListResponse(
        items=[GuardiaResponse.model_validate(g) for g in items],
        total=total,
        pages=pages,
    )


@router.get("/exportar-csv")
async def exportar_csv(
    materia_id: uuid.UUID | None = Query(None),
    carrera_id: uuid.UUID | None = Query(None),
    cohorte_id: uuid.UUID | None = Query(None),
    asignacion_id: uuid.UUID | None = Query(None),
    estado: EstadoGuardia | None = Query(None),
    fecha_desde: date | None = Query(None),
    fecha_hasta: date | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("guardias:ver")),
):
    service = GuardiaService(db, current_user.tenant_id)
    csv_content = await service.exportar_csv(
        materia_id=materia_id,
        carrera_id=carrera_id,
        cohorte_id=cohorte_id,
        asignacion_id=asignacion_id,
        estado=estado,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=guardias.csv",
        },
    )
