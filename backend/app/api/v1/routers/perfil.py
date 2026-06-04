from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.schemas.auth import CurrentUser
from app.schemas.usuario import PerfilOut, PerfilUpdate
from app.services.perfil_service import PerfilService

router = APIRouter(prefix="/api/perfil", tags=["perfil"])


@router.get("", response_model=PerfilOut)
async def get_perfil(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    service = PerfilService(db, current_user.tenant_id, current_user.id)
    return await service.get_perfil()


@router.patch("", response_model=PerfilOut)
async def update_perfil(
    body: PerfilUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    service = PerfilService(db, current_user.tenant_id, current_user.id)
    return await service.update_perfil(body)
