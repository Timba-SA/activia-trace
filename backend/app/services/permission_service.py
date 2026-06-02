import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.role_repository import UsuarioRoleRepository


def has_permission(permissions: set[str], required: str) -> bool:
    return required in permissions


class PermissionService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id

    async def resolve_user_permissions(self, user_id: uuid.UUID) -> frozenset[str]:
        repo = UsuarioRoleRepository(self._session, self._tenant_id)
        roles = await repo.get_user_roles(user_id)
        permissions: set[str] = set()
        for role in roles:
            if role.permissions:
                permissions.update(role.permissions)
        return frozenset(permissions)
