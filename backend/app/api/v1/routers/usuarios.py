import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.auth import CurrentUser
from app.schemas.asignacion import AsignacionListResponse, AsignacionResponse
from app.schemas.usuario import (
    UsuarioDetalleResponse,
    UsuarioListResponse,
    UsuarioResponse,
    UsuarioUpdateRequest,
)
from app.services.asignacion_service import AsignacionService
from app.services.usuario_service import UsuarioService

router = APIRouter(prefix="/api/admin/usuarios", tags=["usuarios"])


@router.get("", response_model=UsuarioListResponse)
async def list_usuarios(
    nombre: str | None = None,
    apellido: str | None = None,
    email: str | None = None,
    legajo: str | None = None,
    is_active: bool | None = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("usuarios:gestionar")),
):
    service = UsuarioService(db, current_user.tenant_id)
    items, total, pages = await service.list(
        nombre=nombre, apellido=apellido, email=email,
        legajo=legajo, is_active=is_active, limit=limit, offset=offset,
    )
    return UsuarioListResponse(
        items=[UsuarioResponse.model_validate(r) for r in items],
        total=total,
        pages=pages,
    )


@router.get("/{usuario_id}", response_model=UsuarioDetalleResponse)
async def get_usuario(
    usuario_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("usuarios:gestionar")),
):
    service = UsuarioService(db, current_user.tenant_id)
    has_ver_pii = "usuarios:ver-pii" in current_user.permissions
    data = await service.get_detalle(usuario_id, has_ver_pii)
    return UsuarioDetalleResponse.model_validate(data)


@router.put("/{usuario_id}", response_model=UsuarioDetalleResponse)
async def update_usuario(
    usuario_id: uuid.UUID,
    body: UsuarioUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("usuarios:gestionar")),
):
    service = UsuarioService(db, current_user.tenant_id)
    usuario = await service.update(usuario_id, body)
    has_ver_pii = "usuarios:ver-pii" in current_user.permissions
    data = await service.get_detalle(usuario_id, has_ver_pii)
    return UsuarioDetalleResponse.model_validate(data)


@router.get("/{usuario_id}/asignaciones", response_model=AsignacionListResponse)
async def get_usuario_asignaciones(
    usuario_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("usuarios:gestionar")),
):
    service = AsignacionService(db, current_user.tenant_id)
    items = await service.list_by_usuario(usuario_id)
    return AsignacionListResponse(
        items=[AsignacionResponse.model_validate(r) for r in items],
        total=len(items),
        pages=1,
    )
