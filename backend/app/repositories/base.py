import math
import uuid
from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from sqlalchemy import Column, func, select, Select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    """Generic repository with tenant-scoped soft-delete support.

    Every query auto-filters by tenant_id and deleted_at IS NULL
    unless overridden via skip_tenant_scope or include_deleted.
    """

    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id

    @property
    def _model(self) -> type[ModelT]:
        raise NotImplementedError

    def _apply_tenant_scope(self, stmt: Select, skip: bool = False) -> Select:
        if not skip:
            stmt = stmt.where(self._model.tenant_id == self._tenant_id)  # type: ignore[attr-defined]
        return stmt

    def _apply_soft_delete_filter(self, stmt: Select, include_deleted: bool = False) -> Select:
        if not include_deleted:
            stmt = stmt.where(self._model.deleted_at.is_(None))  # type: ignore[attr-defined]
        return stmt

    def _build_query(
        self,
        include_deleted: bool = False,
        skip_tenant_scope: bool = False,
    ) -> Select:
        stmt = select(self._model)
        stmt = self._apply_tenant_scope(stmt, skip=skip_tenant_scope)
        stmt = self._apply_soft_delete_filter(stmt, include_deleted=include_deleted)
        return stmt

    async def get(
        self,
        id: uuid.UUID,
        include_deleted: bool = False,
        skip_tenant_scope: bool = False,
    ) -> ModelT:
        stmt = self._build_query(include_deleted=include_deleted, skip_tenant_scope=skip_tenant_scope)
        stmt = stmt.where(self._model.id == id)  # type: ignore[attr-defined]
        result = await self._session.execute(stmt)
        instance = result.scalars().first()
        if instance is None:
            raise NotFoundError(f"{self._model.__name__} with id={id} not found")
        return instance

    async def list(
        self,
        include_deleted: bool = False,
        skip_tenant_scope: bool = False,
        **filters: Any,
    ) -> Sequence[ModelT]:
        stmt = self._build_query(include_deleted=include_deleted, skip_tenant_scope=skip_tenant_scope)
        for attr, value in filters.items():
            column = getattr(self._model, attr, None)
            if column is not None:
                stmt = stmt.where(column == value)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def paginate(
        self,
        limit: int = 20,
        offset: int = 0,
        include_deleted: bool = False,
        skip_tenant_scope: bool = False,
    ) -> tuple[Sequence[ModelT], int, int]:
        stmt = self._build_query(include_deleted=include_deleted, skip_tenant_scope=skip_tenant_scope)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()
        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        items = result.scalars().all()
        pages = max(1, math.ceil(total / limit)) if limit > 0 else 1
        return items, total, pages

    async def create(self, **kwargs: Any) -> ModelT:
        instance = self._model(**kwargs)
        self._session.add(instance)
        await self._session.flush()
        return instance

    async def update(
        self,
        id: uuid.UUID,
        include_deleted: bool = False,
        skip_tenant_scope: bool = False,
        **kwargs: Any,
    ) -> ModelT:
        instance = await self.get(
            id,
            include_deleted=include_deleted,
            skip_tenant_scope=skip_tenant_scope,
        )
        for key, value in kwargs.items():
            if value is not None:
                setattr(instance, key, value)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def soft_delete(
        self,
        id: uuid.UUID,
        skip_tenant_scope: bool = False,
    ) -> None:
        instance = await self.get(id, skip_tenant_scope=skip_tenant_scope)
        stmt = (
            update(self._model)
            .where(self._model.id == id)  # type: ignore[attr-defined]
            .values(deleted_at=func.now())
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def count(
        self,
        include_deleted: bool = False,
        skip_tenant_scope: bool = False,
    ) -> int:
        stmt = select(func.count()).select_from(self._model)
        stmt = self._apply_tenant_scope(stmt, skip=skip_tenant_scope)
        stmt = self._apply_soft_delete_filter(stmt, include_deleted=include_deleted)
        result = await self._session.execute(stmt)
        return result.scalar_one()
