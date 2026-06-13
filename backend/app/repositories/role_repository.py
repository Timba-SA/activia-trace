import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.models.usuario_role import UsuarioRole
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id)

    @property
    def _model(self) -> type[Role]:
        return Role

    async def get_by_name(
        self, name: str, include_deleted: bool = False
    ) -> Role | None:
        stmt = select(Role).where(Role.name == name, Role.tenant_id == self._tenant_id)
        if not include_deleted:
            stmt = stmt.where(Role.deleted_at.is_(None))
        result = await self._session.execute(stmt)
        return result.scalars().first()


class UsuarioRoleRepository:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id

    async def assign_role(self, usuario_id: uuid.UUID, role_id: uuid.UUID) -> UsuarioRole:
        assignment = UsuarioRole(
            usuario_id=usuario_id,
            role_id=role_id,
            tenant_id=self._tenant_id,
        )
        self._session.add(assignment)
        await self._session.flush()
        return assignment

    async def remove_role(self, usuario_id: uuid.UUID, role_id: uuid.UUID) -> None:
        stmt = select(UsuarioRole).where(
            UsuarioRole.usuario_id == usuario_id,
            UsuarioRole.role_id == role_id,
        )
        result = await self._session.execute(stmt)
        assignment = result.scalars().first()
        if assignment:
            await self._session.delete(assignment)
            await self._session.flush()

    async def get_user_roles(self, usuario_id: uuid.UUID) -> list[Role]:
        stmt = (
            select(Role)
            .join(UsuarioRole, Role.id == UsuarioRole.role_id)
            .where(
                UsuarioRole.usuario_id == usuario_id,
                Role.tenant_id == self._tenant_id,
                Role.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_role_ids(self, usuario_id: uuid.UUID) -> list[uuid.UUID]:
        stmt = select(UsuarioRole.role_id).where(
            UsuarioRole.usuario_id == usuario_id,
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_role_names(self, usuario_id: uuid.UUID) -> list[str]:
        from app.models.role import Role
        stmt = (
            select(Role.name)
            .join(UsuarioRole, UsuarioRole.role_id == Role.id)
            .where(
                UsuarioRole.usuario_id == usuario_id,
                UsuarioRole.tenant_id == self._tenant_id,
                Role.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return [row[0] for row in result.all()]

    async def has_role_by_name(self, user_id: uuid.UUID, role_name: str) -> bool:
        from app.models.role import Role
        stmt = (
            select(UsuarioRole)
            .join(Role, UsuarioRole.role_id == Role.id)
            .where(
                UsuarioRole.usuario_id == user_id,
                UsuarioRole.tenant_id == self._tenant_id,
                Role.name == role_name,
                Role.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().first() is not None

    async def has_assignment(self, usuario_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        stmt = select(UsuarioRole).where(
            UsuarioRole.usuario_id == usuario_id,
            UsuarioRole.role_id == role_id,
        )
        result = await self._session.execute(stmt)
        return result.scalars().first() is not None
