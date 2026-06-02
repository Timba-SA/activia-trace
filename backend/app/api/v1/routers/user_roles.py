import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.repositories.role_repository import RoleRepository, UsuarioRoleRepository
from app.schemas.auth import CurrentUser
from app.schemas.role import (
    UserRoleAssignRequest,
    UserRoleResponse,
)

router = APIRouter(prefix="/api", tags=["user-roles"])


def _build_role_repo(db: AsyncSession, tenant_id: uuid.UUID) -> RoleRepository:
    return RoleRepository(db, tenant_id)


def _build_user_role_repo(db: AsyncSession, tenant_id: uuid.UUID) -> UsuarioRoleRepository:
    return UsuarioRoleRepository(db, tenant_id)


@router.get("/users/{user_id}/roles", response_model=list[UserRoleResponse])
async def get_user_roles(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("roles:gestionar")),
):
    repo = _build_user_role_repo(db, current_user.tenant_id)
    roles = await repo.get_user_roles(user_id)
    return [UserRoleResponse.model_validate(r) for r in roles]


@router.post("/users/{user_id}/roles", status_code=status.HTTP_201_CREATED)
async def assign_user_role(
    user_id: uuid.UUID,
    body: UserRoleAssignRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("roles:gestionar")),
):
    role_repo = _build_role_repo(db, current_user.tenant_id)
    try:
        role = await role_repo.get(body.role_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    user_role_repo = _build_user_role_repo(db, current_user.tenant_id)
    already = await user_role_repo.has_assignment(user_id, body.role_id)
    if already:
        return {"detail": "Role already assigned"}

    await user_role_repo.assign_role(user_id, body.role_id)
    return {"detail": "Role assigned"}


@router.delete("/users/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_role(
    user_id: uuid.UUID,
    role_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("roles:gestionar")),
):
    user_role_repo = _build_user_role_repo(db, current_user.tenant_id)
    already = await user_role_repo.has_assignment(user_id, role_id)
    if not already:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")
    await user_role_repo.remove_role(user_id, role_id)
