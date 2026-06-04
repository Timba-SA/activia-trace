import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.audit_log import AuditLogListResponse, AuditLogResponse
from app.schemas.auth import CurrentUser

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/log", response_model=AuditLogListResponse)
async def list_audit_log(
    accion: str | None = None,
    actor_id: uuid.UUID | None = None,
    materia_id: uuid.UUID | None = None,
    desde: datetime | None = None,
    hasta: datetime | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("auditoria:ver")),
):
    repo = AuditLogRepository(db, current_user.tenant_id)
    items, total, pages = await repo.find(
        accion=accion,
        actor_id=actor_id,
        materia_id=materia_id,
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
