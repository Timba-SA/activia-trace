import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.asignacion_repository import AsignacionRepository
from app.schemas.audit_log import AuditLogListResponse, AuditLogResponse
from app.schemas.auth import CurrentUser
from app.schemas.auditoria import (
    MetricaAccionesPorDia,
    MetricaComunicacionesListResponse,
    MetricaPorDocenteListResponse,
    MetricaPorMateriaListResponse,
)
from app.services.auditoria_service import AuditoriaService

router = APIRouter(prefix="/api/auditoria", tags=["auditoria"])


async def _resolve_materias_ids(
    db: AsyncSession,
    current_user: CurrentUser,
) -> list[uuid.UUID] | None:
    if "COORDINADOR" in current_user.roles and "ADMIN" not in current_user.roles:
        asignacion_repo = AsignacionRepository(db, current_user.tenant_id)
        asignaciones = await asignacion_repo.list_by_usuario(current_user.id)
        materia_ids = [a.materia_id for a in asignaciones if a.materia_id is not None]
        return materia_ids if materia_ids else None
    return None


@router.get("/metricas/acciones-por-dia")
async def get_acciones_por_dia(
    desde: datetime | None = None,
    hasta: datetime | None = None,
    materia_id: uuid.UUID | None = None,
    actor_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("auditoria:ver")),
):
    materia_ids = await _resolve_materias_ids(db, current_user)
    service = AuditoriaService(db, current_user.tenant_id)
    items = await service.acciones_por_dia(
        desde=desde, hasta=hasta, materia_id=materia_id,
        materia_ids=materia_ids, actor_id=actor_id,
    )
    return {"items": items}


@router.get("/metricas/por-docente")
async def get_por_docente(
    desde: datetime | None = None,
    hasta: datetime | None = None,
    materia_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("auditoria:ver")),
):
    materia_ids = await _resolve_materias_ids(db, current_user)
    service = AuditoriaService(db, current_user.tenant_id)
    items = await service.por_docente(
        desde=desde, hasta=hasta, materia_id=materia_id,
        materia_ids=materia_ids,
    )
    return MetricaPorDocenteListResponse(items=items)


@router.get("/metricas/por-materia")
async def get_por_materia(
    desde: datetime | None = None,
    hasta: datetime | None = None,
    actor_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("auditoria:ver")),
):
    materia_ids = await _resolve_materias_ids(db, current_user)
    service = AuditoriaService(db, current_user.tenant_id)
    items = await service.por_materia(
        desde=desde, hasta=hasta, actor_id=actor_id,
        materia_ids=materia_ids,
    )
    return MetricaPorMateriaListResponse(items=items)


@router.get("/metricas/comunicaciones")
async def get_comunicaciones(
    desde: datetime | None = None,
    hasta: datetime | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("auditoria:ver")),
):
    service = AuditoriaService(db, current_user.tenant_id)
    items = await service.comunicaciones_por_docente(desde=desde, hasta=hasta)
    return MetricaComunicacionesListResponse(items=items)


@router.get("/ultimas-acciones", response_model=AuditLogListResponse)
async def get_ultimas_acciones(
    accion: str | None = None,
    actor_id: uuid.UUID | None = None,
    materia_id: uuid.UUID | None = None,
    desde: datetime | None = None,
    hasta: datetime | None = None,
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("auditoria:ver")),
):
    materia_ids = await _resolve_materias_ids(db, current_user)
    repo = AuditLogRepository(db, current_user.tenant_id)
    items, total, pages = await repo.find(
        accion=accion,
        actor_id=actor_id,
        materia_id=materia_id,
        materia_ids=materia_ids,
        desde=desde,
        hasta=hasta,
        limit=limit,
        offset=offset,
    )
    return AuditLogListResponse(
        items=[AuditLogResponse.model_validate(r) for r in items],
        total=total,
        pages=pages,
        limit=limit,
        offset=offset,
    )
