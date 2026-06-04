import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.models.encuentro_instancia import EstadoInstancia
from app.schemas.auth import CurrentUser
from app.schemas.encuentro import (
    InstanciaEncuentroCreate,
    InstanciaEncuentroListResponse,
    InstanciaEncuentroResponse,
    InstanciaEncuentroUpdate,
    SlotEncuentroCreate,
    SlotEncuentroListResponse,
    SlotEncuentroResponse,
)
from app.services.encuentro_service import EncuentroService

router = APIRouter(prefix="/api/encuentros", tags=["encuentros"])


@router.post("/slots", response_model=SlotEncuentroResponse, status_code=status.HTTP_201_CREATED)
async def crear_slot(
    body: SlotEncuentroCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("encuentros:gestionar")),
):
    service = EncuentroService(db, current_user.tenant_id)
    return await service.create_slot(body)


@router.post("/instancias", response_model=InstanciaEncuentroResponse, status_code=status.HTTP_201_CREATED)
async def crear_instancia(
    body: InstanciaEncuentroCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("encuentros:gestionar")),
):
    service = EncuentroService(db, current_user.tenant_id)
    return await service.create_instancia_independiente(body)


@router.patch("/instancias/{id}", response_model=InstanciaEncuentroResponse)
async def actualizar_instancia(
    id: uuid.UUID,
    body: InstanciaEncuentroUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("encuentros:gestionar")),
):
    service = EncuentroService(db, current_user.tenant_id)
    return await service.update_instancia(id, body)


@router.get("/slots", response_model=SlotEncuentroListResponse)
async def listar_slots(
    materia_id: uuid.UUID | None = Query(None),
    asignacion_id: uuid.UUID | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("encuentros:ver")),
):
    service = EncuentroService(db, current_user.tenant_id)
    items, total, pages = await service.list_slots(
        materia_id=materia_id,
        asignacion_id=asignacion_id,
        limit=limit,
        offset=offset,
    )
    return SlotEncuentroListResponse(
        items=[SlotEncuentroResponse.model_validate(s) for s in items],
        total=total,
        pages=pages,
    )


@router.get("/slots/{id}/instancias", response_model=InstanciaEncuentroListResponse)
async def listar_instancias_por_slot(
    id: uuid.UUID,
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("encuentros:ver")),
):
    service = EncuentroService(db, current_user.tenant_id)
    items, total, pages = await service.list_instancias_por_slot(
        slot_id=id,
        limit=limit,
        offset=offset,
    )
    return InstanciaEncuentroListResponse(
        items=[InstanciaEncuentroResponse.model_validate(i) for i in items],
        total=total,
        pages=pages,
    )


@router.get("/instancias", response_model=InstanciaEncuentroListResponse)
async def listar_instancias_admin(
    materia_id: uuid.UUID | None = Query(None),
    estado: EstadoInstancia | None = Query(None),
    fecha_desde: date | None = Query(None),
    fecha_hasta: date | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("encuentros:ver")),
):
    service = EncuentroService(db, current_user.tenant_id)
    items, total, pages = await service.list_instancias_admin(
        materia_id=materia_id,
        estado=estado,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        limit=limit,
        offset=offset,
    )
    return InstanciaEncuentroListResponse(
        items=[InstanciaEncuentroResponse.model_validate(i) for i in items],
        total=total,
        pages=pages,
    )


@router.get("/exportar-html", response_class=HTMLResponse)
async def exportar_html(
    materia_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("encuentros:ver")),
):
    service = EncuentroService(db, current_user.tenant_id)
    html = await service.exportar_html(materia_id=materia_id)
    return HTMLResponse(content=html, media_type="text/html")
