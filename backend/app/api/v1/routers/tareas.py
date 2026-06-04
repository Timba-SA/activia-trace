import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import CurrentUser
from app.schemas.tarea import (
    ComentarioTareaCreate,
    ComentarioTareaResponse,
    TareaCreate,
    TareaListResponse,
    TareaResponse,
    TareaUpdate,
)
from app.services.tarea_service import TareasService

router = APIRouter(prefix="/api/tareas", tags=["tareas"])

_ROLES_COORDINADOR_ADMIN = {"COORDINADOR", "ADMIN"}


def _require_coordinador_admin(current_user: CurrentUser) -> None:
    roles_upper = {r.upper() for r in current_user.roles}
    if not roles_upper & _ROLES_COORDINADOR_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol COORDINADOR o ADMIN",
        )


@router.get("/", response_model=TareaListResponse)
async def listar_mis_tareas(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("tareas:gestionar")),
):
    service = TareasService(
        db, current_user.tenant_id, current_user.id, current_user.roles
    )
    items, total = await service.listar_mis_tareas(
        usuario_id=current_user.id, limit=limit, offset=offset
    )
    return TareaListResponse(
        items=items, total=total, page=offset // limit + 1, page_size=limit
    )


@router.post("/", response_model=TareaResponse, status_code=status.HTTP_201_CREATED)
async def crear_tarea(
    body: TareaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("tareas:gestionar")),
):
    service = TareasService(
        db, current_user.tenant_id, current_user.id, current_user.roles
    )
    return await service.crear_tarea(body, current_user.id)


@router.get("/admin", response_model=TareaListResponse)
async def listar_tareas_admin(
    asignado_a: uuid.UUID | None = Query(None),
    asignado_por: uuid.UUID | None = Query(None),
    materia_id: uuid.UUID | None = Query(None),
    estado: str | None = Query(None),
    q: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("tareas:gestionar")),
):
    _require_coordinador_admin(current_user)
    service = TareasService(
        db, current_user.tenant_id, current_user.id, current_user.roles
    )
    filtros = {}
    if asignado_a:
        filtros["asignado_a"] = asignado_a
    if asignado_por:
        filtros["asignado_por"] = asignado_por
    if materia_id:
        filtros["materia_id"] = materia_id
    if estado:
        filtros["estado"] = estado
    if q:
        filtros["q"] = q
    items, total = await service.listar_tareas_admin(
        filtros=filtros, limit=limit, offset=offset
    )
    return TareaListResponse(
        items=items, total=total, page=offset // limit + 1, page_size=limit
    )


@router.get("/{id}", response_model=TareaResponse)
async def obtener_tarea(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("tareas:gestionar")),
):
    service = TareasService(
        db, current_user.tenant_id, current_user.id, current_user.roles
    )
    return await service.obtener_tarea(id)


@router.patch("/{id}", response_model=TareaResponse)
async def actualizar_tarea(
    id: uuid.UUID,
    body: TareaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("tareas:gestionar")),
):
    service = TareasService(
        db, current_user.tenant_id, current_user.id, current_user.roles
    )
    if body.estado is not None and body.estado != (
        await service.obtener_tarea(id)
    ).estado:
        return await service.cambiar_estado(id, body.estado)
    return await service.actualizar_tarea(id, body)


@router.post(
    "/{id}/comentarios",
    response_model=ComentarioTareaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def agregar_comentario(
    id: uuid.UUID,
    body: ComentarioTareaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("tareas:gestionar")),
):
    service = TareasService(
        db, current_user.tenant_id, current_user.id, current_user.roles
    )
    return await service.agregar_comentario(id, current_user.id, body.texto)


@router.get("/{id}/comentarios", response_model=list[ComentarioTareaResponse])
async def listar_comentarios(
    id: uuid.UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("tareas:gestionar")),
):
    service = TareasService(
        db, current_user.tenant_id, current_user.id, current_user.roles
    )
    items, total = await service.listar_comentarios(
        tarea_id=id, limit=limit, offset=offset
    )
    return items
