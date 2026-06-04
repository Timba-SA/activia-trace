from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.guardia import EstadoGuardia, Guardia
from app.repositories.base import BaseRepository


class GuardiaRepository(BaseRepository[Guardia]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id)
        # Guardia has no soft delete, so skip the deleted_at filter
        self._include_deleted_override = True

    @property
    def _model(self) -> type[Guardia]:
        return Guardia

    # override to skip soft-delete filter since Guardia has no deleted_at
    def _apply_soft_delete_filter(self, stmt, include_deleted=False):
        return stmt

    async def list_by_usuario(
        self,
        asignacion_ids: list[uuid.UUID],
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Guardia], int, int]:
        stmt = select(Guardia).where(
            Guardia.tenant_id == self._tenant_id,
            Guardia.asignacion_id.in_(asignacion_ids),
        )
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()
        stmt = stmt.limit(limit).offset(offset).order_by(Guardia.creada_at.desc())
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())
        pages = max(1, (total + limit - 1) // limit) if limit > 0 else 1
        return items, total, pages

    async def list_admin(
        self,
        materia_id: uuid.UUID | None = None,
        carrera_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        asignacion_id: uuid.UUID | None = None,
        estado: EstadoGuardia | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Guardia], int, int]:
        stmt = select(Guardia).where(Guardia.tenant_id == self._tenant_id)
        if materia_id is not None:
            stmt = stmt.where(Guardia.materia_id == materia_id)
        if carrera_id is not None:
            stmt = stmt.where(Guardia.carrera_id == carrera_id)
        if cohorte_id is not None:
            stmt = stmt.where(Guardia.cohorte_id == cohorte_id)
        if asignacion_id is not None:
            stmt = stmt.where(Guardia.asignacion_id == asignacion_id)
        if estado is not None:
            stmt = stmt.where(Guardia.estado == estado)
        if fecha_desde is not None:
            stmt = stmt.where(Guardia.creada_at >= fecha_desde)
        if fecha_hasta is not None:
            stmt = stmt.where(Guardia.creada_at <= fecha_hasta)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()
        stmt = stmt.limit(limit).offset(offset).order_by(Guardia.creada_at.desc())
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())
        pages = max(1, (total + limit - 1) // limit) if limit > 0 else 1
        return items, total, pages

    async def list_for_export(
        self,
        materia_id: uuid.UUID | None = None,
        carrera_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        asignacion_id: uuid.UUID | None = None,
        estado: EstadoGuardia | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> Sequence[Guardia]:
        stmt = select(Guardia).where(Guardia.tenant_id == self._tenant_id)
        if materia_id is not None:
            stmt = stmt.where(Guardia.materia_id == materia_id)
        if carrera_id is not None:
            stmt = stmt.where(Guardia.carrera_id == carrera_id)
        if cohorte_id is not None:
            stmt = stmt.where(Guardia.cohorte_id == cohorte_id)
        if asignacion_id is not None:
            stmt = stmt.where(Guardia.asignacion_id == asignacion_id)
        if estado is not None:
            stmt = stmt.where(Guardia.estado == estado)
        if fecha_desde is not None:
            stmt = stmt.where(Guardia.creada_at >= fecha_desde)
        if fecha_hasta is not None:
            stmt = stmt.where(Guardia.creada_at <= fecha_hasta)
        stmt = stmt.order_by(Guardia.creada_at.desc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, **kwargs):
        instance = self._model(**kwargs)
        self._session.add(instance)
        await self._session.flush()
        return instance

    async def get(
        self,
        id: uuid.UUID,
        include_deleted: bool = False,
        skip_tenant_scope: bool = False,
    ) -> Guardia:
        stmt = select(self._model).where(self._model.id == id)
        if not skip_tenant_scope:
            stmt = stmt.where(self._model.tenant_id == self._tenant_id)
        result = await self._session.execute(stmt)
        instance = result.scalars().first()
        if instance is None:
            from app.core.exceptions import NotFoundError
            raise NotFoundError(f"Guardia with id={id} not found")
        return instance

    async def update(
        self,
        id: uuid.UUID,
        include_deleted: bool = False,
        skip_tenant_scope: bool = False,
        **kwargs,
    ) -> Guardia:
        instance = await self.get(id, skip_tenant_scope=skip_tenant_scope)
        for key, value in kwargs.items():
            if value is not None:
                setattr(instance, key, value)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance
