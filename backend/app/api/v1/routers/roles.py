import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.repositories.role_repository import RoleRepository
from app.schemas.auth import CurrentUser
from app.schemas.role import (
    RoleCreate,
    RoleListResponse,
    RoleResponse,
    RoleUpdate,
)

router = APIRouter(prefix="/api", tags=["roles"])


@router.get("/roles", response_model=RoleListResponse)
async def list_roles(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("roles:gestionar")),
):
    repo = RoleRepository(db, current_user.tenant_id)
    items, total, pages = await repo.paginate(limit=limit, offset=offset)
    return RoleListResponse(
        items=[RoleResponse.model_validate(r) for r in items],
        total=total,
        pages=pages,
    )


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("roles:gestionar")),
):
    repo = RoleRepository(db, current_user.tenant_id)
    try:
        role = await repo.get(role_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return RoleResponse.model_validate(role)


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    body: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("roles:gestionar")),
):
    repo = RoleRepository(db, current_user.tenant_id)
    existing = await repo.get_by_name(body.name)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role name already exists")
    role = await repo.create(
        tenant_id=current_user.tenant_id,
        name=body.name,
        description=body.description,
        permissions=body.permissions,
        is_system_role=False,
    )
    return RoleResponse.model_validate(role)


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: uuid.UUID,
    body: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("roles:gestionar")),
):
    repo = RoleRepository(db, current_user.tenant_id)
    try:
        role = await repo.get(role_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    if body.name is not None:
        role.name = body.name
    if body.description is not None:
        role.description = body.description
    if body.permissions is not None:
        role.permissions = body.permissions
    await db.flush()
    await db.refresh(role)
    return RoleResponse.model_validate(role)


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("roles:gestionar")),
):
    repo = RoleRepository(db, current_user.tenant_id)
    try:
        role = await repo.get(role_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    if role.is_system_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete a system role",
        )
    await repo.soft_delete(role_id)
