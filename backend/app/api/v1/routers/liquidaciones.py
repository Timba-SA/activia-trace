import uuid

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import CurrentUser
from app.schemas.factura import FacturaCreate, FacturaEstadoUpdate, FacturaListResponse, FacturaResponse
from app.schemas.liquidacion import (
    ExportarRequest,
    LiquidacionCalcularRequest,
    LiquidacionCerrarResponse,
    LiquidacionHistorialResponse,
    LiquidacionListResponse,
    LiquidacionResponse,
)
from app.schemas.materia_grupo_plus import (
    MateriaGrupoPlusCreate,
    MateriaGrupoPlusResponse,
    MateriaGrupoPlusUpdate,
)
from app.schemas.salario_base import (
    SalarioBaseCreate,
    SalarioBaseResponse,
    SalarioBaseUpdate,
)
from app.schemas.salario_plus import (
    SalarioPlusCreate,
    SalarioPlusResponse,
    SalarioPlusUpdate,
)
from app.services.factura_service import FacturaService
from app.services.grilla_service import GrillaService
from app.services.liquidacion_service import LiquidacionService

router = APIRouter(prefix="/api/liquidaciones", tags=["liquidaciones"])


# ──────────────────────────────────────────
# Liquidacion endpoints
# ──────────────────────────────────────────


@router.post("/calcular", response_model=LiquidacionListResponse, status_code=status.HTTP_201_CREATED)
async def calcular_liquidacion(
    body: LiquidacionCalcularRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("liquidaciones:calcular")),
):
    service = LiquidacionService(db, current_user.tenant_id, current_user.id)
    items = await service.calcular(body)
    return LiquidacionListResponse(
        items=items,
        total=len(items),
        page=1,
        page_size=len(items),
    )


@router.get("/historial", response_model=LiquidacionHistorialResponse)
async def historial_liquidaciones(
    cohorte_id: uuid.UUID | None = None,
    periodo: str | None = None,
    usuario_id: uuid.UUID | None = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("liquidaciones:ver")),
):
    service = LiquidacionService(db, current_user.tenant_id, current_user.id)
    items, total = await service.historial(
        cohorte_id=cohorte_id,
        periodo=periodo,
        usuario_id=usuario_id,
        limit=limit,
        offset=offset,
    )
    page = (offset // limit) + 1
    return LiquidacionHistorialResponse(items=items, total=total, page=page, page_size=limit)


@router.post("/exportar")
async def exportar_liquidaciones(
    body: ExportarRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("liquidaciones:exportar")),
):
    service = LiquidacionService(db, current_user.tenant_id, current_user.id)
    csv_content = await service.exportar(body)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=liquidaciones_{body.periodo}.csv"},
    )


@router.get("", response_model=LiquidacionListResponse)
async def list_liquidaciones(
    cohorte_id: uuid.UUID | None = None,
    periodo: str | None = None,
    usuario_id: uuid.UUID | None = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("liquidaciones:ver")),
):
    service = LiquidacionService(db, current_user.tenant_id, current_user.id)
    items, total = await service.listar(
        cohorte_id=cohorte_id,
        periodo=periodo,
        usuario_id=usuario_id,
        limit=limit,
        offset=offset,
    )
    page = (offset // limit) + 1
    return LiquidacionListResponse(items=items, total=total, page=page, page_size=limit)


@router.get("/{liquidacion_id}", response_model=LiquidacionResponse)
async def get_liquidacion(
    liquidacion_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("liquidaciones:ver")),
):
    service = LiquidacionService(db, current_user.tenant_id, current_user.id)
    return await service.obtener(liquidacion_id)


@router.post("/{liquidacion_id}/cerrar", response_model=LiquidacionCerrarResponse)
async def cerrar_liquidacion(
    liquidacion_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("liquidaciones:cerrar")),
):
    ip = request.client.host if request.client else ""
    user_agent = request.headers.get("user-agent", "")
    service = LiquidacionService(db, current_user.tenant_id, current_user.id)
    return await service.cerrar(
        liquidacion_id, actor_id=current_user.id, ip=ip, user_agent=user_agent,
    )


# ──────────────────────────────────────────
# Grilla Salarial — SalarioBase
# ──────────────────────────────────────────


@router.get("/salarios-base", response_model=list[SalarioBaseResponse])
async def list_salarios_base(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("liquidaciones:configurar-salarios")),
):
    service = GrillaService(db, current_user.tenant_id)
    return await service.listar_salarios_base()


@router.post("/salarios-base", response_model=SalarioBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_salario_base(
    body: SalarioBaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("liquidaciones:configurar-salarios")),
):
    service = GrillaService(db, current_user.tenant_id)
    return await service.crear_salario_base(body)


@router.put("/salarios-base/{id}", response_model=SalarioBaseResponse)
async def update_salario_base(
    id: uuid.UUID,
    body: SalarioBaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("liquidaciones:configurar-salarios")),
):
    service = GrillaService(db, current_user.tenant_id)
    return await service.actualizar_salario_base(id, body)


@router.delete("/salarios-base/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_salario_base(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("liquidaciones:configurar-salarios")),
):
    service = GrillaService(db, current_user.tenant_id)
    await service.eliminar_salario_base(id)


# ──────────────────────────────────────────
# Grilla Salarial — SalarioPlus
# ──────────────────────────────────────────


@router.get("/plus", response_model=list[SalarioPlusResponse])
async def list_salarios_plus(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("liquidaciones:configurar-salarios")),
):
    service = GrillaService(db, current_user.tenant_id)
    return await service.listar_salarios_plus()


@router.post("/plus", response_model=SalarioPlusResponse, status_code=status.HTTP_201_CREATED)
async def create_salario_plus(
    body: SalarioPlusCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("liquidaciones:configurar-salarios")),
):
    service = GrillaService(db, current_user.tenant_id)
    return await service.crear_salario_plus(body)


@router.put("/plus/{id}", response_model=SalarioPlusResponse)
async def update_salario_plus(
    id: uuid.UUID,
    body: SalarioPlusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("liquidaciones:configurar-salarios")),
):
    service = GrillaService(db, current_user.tenant_id)
    return await service.actualizar_salario_plus(id, body)


@router.delete("/plus/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_salario_plus(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("liquidaciones:configurar-salarios")),
):
    service = GrillaService(db, current_user.tenant_id)
    await service.eliminar_salario_plus(id)


# ──────────────────────────────────────────
# Grilla Salarial — MateriaGrupoPlus
# ──────────────────────────────────────────


@router.get("/materias-grupo", response_model=list[MateriaGrupoPlusResponse])
async def list_materias_grupo(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("liquidaciones:configurar-salarios")),
):
    service = GrillaService(db, current_user.tenant_id)
    return await service.listar_materias_grupo()


@router.post("/materias-grupo", response_model=MateriaGrupoPlusResponse, status_code=status.HTTP_201_CREATED)
async def create_materia_grupo(
    body: MateriaGrupoPlusCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("liquidaciones:configurar-salarios")),
):
    service = GrillaService(db, current_user.tenant_id)
    return await service.crear_materia_grupo(body)


@router.put("/materias-grupo/{id}", response_model=MateriaGrupoPlusResponse)
async def update_materia_grupo(
    id: uuid.UUID,
    body: MateriaGrupoPlusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("liquidaciones:configurar-salarios")),
):
    service = GrillaService(db, current_user.tenant_id)
    return await service.actualizar_materia_grupo(id, body)


@router.delete("/materias-grupo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_materia_grupo(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("liquidaciones:configurar-salarios")),
):
    service = GrillaService(db, current_user.tenant_id)
    await service.eliminar_materia_grupo(id)
