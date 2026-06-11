"""Dependency injection para active-trace."""

import uuid
from collections.abc import AsyncGenerator

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_factory
from app.core.security import decode_token
from app.core.tenancy import resolve_tenant_from_slug
from app.models.usuario import Usuario
from app.repositories.role_repository import UsuarioRoleRepository
from app.schemas.auth import CurrentUser

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    factory = get_factory()
    session = factory()
    try:
        yield session
        await session.commit()
    except HTTPException:
        await session.commit()
        raise
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_tenant(
    x_tenant_slug: str = Header(..., description="Tenant slug de la institución"),
    db: AsyncSession = Depends(get_db),  # type: ignore[arg-type]
) -> uuid.UUID:
    """Resolve tenant_id from X-Tenant-Slug header.

    Returns the tenant UUID for repository scoping.
    """
    try:
        tenant = await resolve_tenant_from_slug(db, x_tenant_slug)
    except Exception as exc:
        raise HTTPException(status_code=403, detail="Invalid or inactive tenant") from exc
    return tenant.id


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),  # type: ignore[arg-type]
) -> CurrentUser:
    """Extract and verify JWT from Authorization header.

    Returns a CurrentUser derived exclusively from the token.
    Identity cannot be overridden by request parameters.
    Permissions are resolved server-side from role assignments.

    Detects impersonation tokens and populates request.state
    with impersonation context for downstream dependencies.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
        )

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
        )

    stmt = select(Usuario).where(Usuario.id == user_uuid)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not active or not found",
        )

    tenant_id = payload.get("tenant_id")
    tenant_uuid = uuid.UUID(tenant_id) if tenant_id else user.tenant_id

    # Detect impersonation
    is_impersonation = payload.get("impersonation", False)
    if is_impersonation:
        request.state.impersonation = True
        request.state.impersonating_user_id = payload.get("impersonating_user_id")
    else:
        request.state.impersonation = False

    role_repo = UsuarioRoleRepository(db, tenant_uuid)
    roles = await role_repo.get_user_roles(user_uuid)
    permissions: set[str] = set()
    for role in roles:
        if role.permissions:
            permissions.update(role.permissions)

    return CurrentUser(
        id=user.id,
        tenant_id=tenant_uuid,
        email=user.email,
        roles=list({role.name for role in roles}),
        permissions=frozenset(permissions),
        is_active=user.is_active,
    )


def require_permission(permission: str):
    """Factory that returns a FastAPI dependency checking for a specific permission.

    Usage:
        @router.get("/endpoint")
        async def handler(current_user: CurrentUser = Depends(require_permission("modulo:accion"))):
            ...
    """
    async def _check(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )
        return current_user
    return _check
