import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.auth import CurrentUser
from app.schemas.coloquio import (
    ResultadoBatchCreate,
    ResultadoCreate,
    ResultadoResponse,
)
from app.services.coloquio_service import ColoquioService

router = APIRouter(prefix="/api/coloquios/resultados", tags=["coloquios"])


@router.post("", response_model=ResultadoResponse, status_code=status.HTTP_201_CREATED)
async def registrar_resultado(
    evaluacion_id: uuid.UUID,
    body: ResultadoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("coloquios:gestionar")),
):
    service = ColoquioService(db, current_user.tenant_id, current_user.id)
    return await service.registrar_resultado(
        evaluacion_id, body.alumno_id, body.nota_final
    )


@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def registrar_resultados_batch(
    evaluacion_id: uuid.UUID,
    body: ResultadoBatchCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("coloquios:gestionar")),
):
    service = ColoquioService(db, current_user.tenant_id, current_user.id)
    items = [item.model_dump() for item in body.items]
    return await service.registrar_resultados_batch(evaluacion_id, items)


@router.get("", response_model=list[ResultadoResponse])
async def listar_resultados(
    evaluacion_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("coloquios:ver")),
):
    from app.repositories.coloquio_repository import ResultadoEvaluacionRepository
    repo = ResultadoEvaluacionRepository(db, current_user.tenant_id)
    resultados = await repo.list_by_evaluacion(evaluacion_id)
    return [ResultadoResponse.model_validate(r) for r in resultados]
