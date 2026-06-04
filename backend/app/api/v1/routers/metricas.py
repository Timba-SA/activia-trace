from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.auth import CurrentUser
from app.schemas.coloquio import MetricasResponse
from app.services.coloquio_service import ColoquioService

router = APIRouter(prefix="/api/coloquios/metricas", tags=["coloquios"])


@router.get("", response_model=MetricasResponse)
async def obtener_metricas(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("coloquios:ver")),
):
    service = ColoquioService(db, current_user.tenant_id, current_user.id)
    return await service.obtener_metricas()
