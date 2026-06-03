import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user, require_permission
from app.schemas.analisis import (
    AtrasadosResponse,
    EntregasSinCorregirResponse,
    MonitorFiltros,
    MonitorResponse,
    NotasFinalesRequest,
    NotasFinalesResponse,
    RankingResponse,
    ReporteRapidoResponse,
)
from app.schemas.auth import CurrentUser
from app.services.analisis_service import AnalisisService

router = APIRouter(prefix="/api/v1", tags=["analisis"])


@router.get("/analisis/atrasados", response_model=AtrasadosResponse)
async def get_atrasados(
    materia_id: uuid.UUID = Query(...),
    cohorte_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("atrasados:ver")),
):
    service = AnalisisService(db, current_user.tenant_id, current_user.id)
    result = await service.get_atrasados(materia_id, cohorte_id)
    return AtrasadosResponse(**result)


@router.get("/analisis/ranking", response_model=RankingResponse)
async def get_ranking(
    materia_id: uuid.UUID = Query(...),
    cohorte_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("atrasados:ver")),
):
    service = AnalisisService(db, current_user.tenant_id, current_user.id)
    result = await service.get_ranking(materia_id, cohorte_id)
    return RankingResponse(**result)


@router.get("/analisis/reporte-rapido", response_model=ReporteRapidoResponse)
async def get_reporte_rapido(
    materia_id: uuid.UUID = Query(...),
    cohorte_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("atrasados:ver")),
):
    service = AnalisisService(db, current_user.tenant_id, current_user.id)
    result = await service.get_reporte_rapido(materia_id, cohorte_id)
    return ReporteRapidoResponse(**result)


@router.post("/analisis/notas-finales", response_model=NotasFinalesResponse)
async def get_notas_finales(
    body: NotasFinalesRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("atrasados:ver")),
):
    if not body.grupos:
        raise HTTPException(status_code=400, detail="At least one activity group is required")
    service = AnalisisService(db, current_user.tenant_id, current_user.id)
    result = await service.get_notas_finales(
        body.materia_id, body.cohorte_id, body.grupos,
    )
    return NotasFinalesResponse(**result)


@router.get("/analisis/monitor", response_model=MonitorResponse)
async def get_monitor(
    materia_id: uuid.UUID | None = Query(default=None),
    cohorte_id: uuid.UUID | None = Query(default=None),
    alumno: str | None = Query(default=None),
    email: str | None = Query(default=None),
    actividad: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("atrasados:ver")),
):
    service = AnalisisService(db, current_user.tenant_id, current_user.id)
    result = await service.get_monitor(
        materia_id=materia_id,
        cohorte_id=cohorte_id,
        alumno=alumno,
        email=email,
        actividad=actividad,
        page=page,
        limit=limit,
    )
    return MonitorResponse(**result)


@router.get("/analisis/entregas-sin-corregir", response_model=EntregasSinCorregirResponse)
async def get_entregas_sin_corregir(
    materia_id: uuid.UUID = Query(...),
    cohorte_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("atrasados:ver")),
):
    service = AnalisisService(db, current_user.tenant_id, current_user.id)
    result = await service.get_entregas_sin_corregir(materia_id, cohorte_id)
    return EntregasSinCorregirResponse(**result)


@router.get("/analisis/entregas-sin-corregir/export")
async def export_entregas_sin_corregir(
    materia_id: uuid.UUID = Query(...),
    cohorte_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("atrasados:ver")),
):
    service = AnalisisService(db, current_user.tenant_id, current_user.id)
    csv_content = await service.export_entregas_sin_corregir_csv(materia_id, cohorte_id)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=entregas-sin-corregir-{materia_id}.csv"},
    )
