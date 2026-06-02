import uuid
from collections.abc import Sequence

from sqlalchemy import func, select, Select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.tenant import Tenant
from app.repositories.base import BaseRepository


class TenantRepository(BaseRepository[Tenant]):
    """Repository for Tenant model — the root multi-tenancy entity.

    TenantRepository does NOT apply tenant-scope (Tenant is the root).
    Soft-delete and all other BaseRepository patterns still apply.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, tenant_id=uuid.UUID(int=0))
        self._session = session

    @property
    def _model(self) -> type[Tenant]:
        return Tenant

    def _apply_tenant_scope(self, stmt: Select, skip: bool = False) -> Select:
        return stmt

    async def get_by_slug(self, slug: str, include_deleted: bool = False) -> Tenant:
        stmt = select(Tenant).where(Tenant.slug == slug)
        stmt = self._apply_soft_delete_filter(stmt, include_deleted=include_deleted)
        result = await self._session.execute(stmt)
        instance = result.scalars().first()
        if instance is None:
            raise NotFoundError(f"Tenant with slug={slug} not found")
        return instance

    async def get_by_code(self, code: str, include_deleted: bool = False) -> Tenant:
        stmt = select(Tenant).where(Tenant.code == code)
        stmt = self._apply_soft_delete_filter(stmt, include_deleted=include_deleted)
        result = await self._session.execute(stmt)
        instance = result.scalars().first()
        if instance is None:
            raise NotFoundError(f"Tenant with code={code} not found")
        return instance

    async def create(self, **kwargs) -> Tenant:
        instance = Tenant(**kwargs)
        self._session.add(instance)
        await self._session.flush()
        return instance

    async def soft_delete(self, id: uuid.UUID, skip_tenant_scope: bool = True) -> None:
        await self.get(id, include_deleted=False)
        stmt = (
            update(Tenant)
            .where(Tenant.id == id)
            .values(deleted_at=func.now())
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def list(
        self,
        include_deleted: bool = False,
        skip_tenant_scope: bool = True,
        **filters,
    ) -> Sequence[Tenant]:
        return await super().list(
            include_deleted=include_deleted,
            skip_tenant_scope=skip_tenant_scope,
            **filters,
        )

    async def count(
        self,
        include_deleted: bool = False,
        skip_tenant_scope: bool = True,
    ) -> int:
        return await super().count(
            include_deleted=include_deleted,
            skip_tenant_scope=skip_tenant_scope,
        )

    async def paginate(
        self,
        limit: int = 20,
        offset: int = 0,
        include_deleted: bool = False,
        skip_tenant_scope: bool = True,
    ) -> tuple[Sequence[Tenant], int, int]:
        return await super().paginate(
            limit=limit,
            offset=offset,
            include_deleted=include_deleted,
            skip_tenant_scope=skip_tenant_scope,
        )
