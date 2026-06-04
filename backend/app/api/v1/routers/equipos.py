import uuid

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.asignacion import (
    AsignacionDocenteListResponse,
    AsignacionDocenteResponse,
    AsignacionMasivaRequest,
    BulkOperationResponse,
    CloneRequest,
    VigenciaUpdateRequest,
)
from app.schemas.auth import CurrentUser
from app.services.asignacion_service import AsignacionService

router = APIRouter(prefix="/api/equipos", tags=["equipos"])


@router.get("/mis-equipos", response_model=AsignacionDocenteListResponse)
async def mis_equipos(
    estado: str | None = Query(None),
    materia_id: uuid.UUID | None = Query(None),
    rol: str | None = Query(None),
    carrera_id: uuid.UUID | None = Query(None),
    cohorte_id: uuid.UUID | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("equipos:ver")),
):
    service = AsignacionService(db, current_user.tenant_id)
    items, total, pages = await service.mis_equipos(
        usuario_id=current_user.id,
        estado=estado,
        materia_id=materia_id,
        rol=rol,
        carrera_id=carrera_id,
        cohorte_id=cohorte_id,
        limit=limit,
        offset=offset,
    )
    return AsignacionDocenteListResponse(
        items=[_to_docente_response(a) for a in items],
        total=total,
        pages=pages,
    )


@router.get("", response_model=AsignacionDocenteListResponse)
async def list_equipos(
    materia_id: uuid.UUID | None = Query(None),
    carrera_id: uuid.UUID | None = Query(None),
    cohorte_id: uuid.UUID | None = Query(None),
    usuario_id: uuid.UUID | None = Query(None),
    nombre: str | None = Query(None),
    rol: str | None = Query(None),
    responsable_id: uuid.UUID | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("equipos:ver")),
):
    service = AsignacionService(db, current_user.tenant_id)
    items, total, pages = await service.list_equipos(
        materia_id=materia_id,
        carrera_id=carrera_id,
        cohorte_id=cohorte_id,
        usuario_id=usuario_id,
        nombre=nombre,
        rol=rol,
        responsable_id=responsable_id,
        limit=limit,
        offset=offset,
    )
    return AsignacionDocenteListResponse(
        items=[_to_docente_response(a) for a in items],
        total=total,
        pages=pages,
    )


@router.post("/asignacion-masiva", response_model=BulkOperationResponse, status_code=status.HTTP_201_CREATED)
async def asignacion_masiva(
    body: AsignacionMasivaRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("equipos:asignar")),
):
    service = AsignacionService(db, current_user.tenant_id)
    created = await service.asignacion_masiva(body)
    return BulkOperationResponse(creadas=len(created))


@router.post("/clonar", response_model=BulkOperationResponse)
async def clonar_equipo(
    body: CloneRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("equipos:asignar")),
):
    service = AsignacionService(db, current_user.tenant_id)
    created = await service.clonar(body)
    return BulkOperationResponse(creadas=len(created))


@router.patch("/vigencia", response_model=BulkOperationResponse)
async def update_vigencia(
    body: VigenciaUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("equipos:asignar")),
):
    service = AsignacionService(db, current_user.tenant_id)
    affected = await service.update_vigencia_equipo(body)
    return BulkOperationResponse(afectadas=affected)


@router.get("/exportar")
async def exportar_equipo(
    materia_id: uuid.UUID = Query(...),
    carrera_id: uuid.UUID = Query(...),
    cohorte_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("equipos:ver")),
):
    service = AsignacionService(db, current_user.tenant_id)
    csv_content = await service.exportar_equipo(
        materia_id=materia_id,
        carrera_id=carrera_id,
        cohorte_id=cohorte_id,
    )
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="equipo-{materia_id}.csv"',
        },
    )


def _to_docente_response(a) -> AsignacionDocenteResponse:
    nombre = getattr(a, "nombre", None)
    apellido = getattr(a, "apellido", None)
    return AsignacionDocenteResponse(
        id=a.id,
        usuario_id=a.usuario_id,
        nombre=nombre,
        apellido=apellido,
        rol=a.rol,
        carrera_id=a.carrera_id,
        materia_id=a.materia_id,
        cohorte_id=a.cohorte_id,
        responsable_id=a.responsable_id,
        fecha_inicio=a.fecha_inicio,
        fecha_fin=a.fecha_fin,
        comisiones=a.comisiones or [],
        is_active=a.is_active,
    )
