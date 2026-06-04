from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.encuentro_instancia import EstadoInstancia, InstanciaEncuentro
from app.models.encuentro_slot import SlotEncuentro
from app.repositories.base import BaseRepository


class SlotEncuentroRepository(BaseRepository[SlotEncuentro]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id)

    @property
    def _model(self) -> type[SlotEncuentro]:
        return SlotEncuentro

    async def list_by_filters(
        self,
        materia_id: uuid.UUID | None = None,
        asignacion_id: uuid.UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[SlotEncuentro], int, int]:
        stmt = select(SlotEncuentro).where(
            SlotEncuentro.tenant_id == self._tenant_id,
            SlotEncuentro.deleted_at.is_(None),
        )
        if materia_id is not None:
            stmt = stmt.where(SlotEncuentro.materia_id == materia_id)
        if asignacion_id is not None:
            stmt = stmt.where(SlotEncuentro.asignacion_id == asignacion_id)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()
        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())
        pages = max(1, (total + limit - 1) // limit) if limit > 0 else 1
        return items, total, pages


class InstanciaEncuentroRepository(BaseRepository[InstanciaEncuentro]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id)

    @property
    def _model(self) -> type[InstanciaEncuentro]:
        return InstanciaEncuentro

    async def list_by_slot(
        self,
        slot_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[InstanciaEncuentro], int, int]:
        stmt = (
            select(InstanciaEncuentro)
            .where(
                InstanciaEncuentro.tenant_id == self._tenant_id,
                InstanciaEncuentro.deleted_at.is_(None),
                InstanciaEncuentro.slot_id == slot_id,
            )
            .order_by(InstanciaEncuentro.fecha.asc())
        )
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()
        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())
        pages = max(1, (total + limit - 1) // limit) if limit > 0 else 1
        return items, total, pages

    async def list_admin(
        self,
        materia_id: uuid.UUID | None = None,
        estado: EstadoInstancia | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[InstanciaEncuentro], int, int]:
        stmt = select(InstanciaEncuentro).where(
            InstanciaEncuentro.tenant_id == self._tenant_id,
            InstanciaEncuentro.deleted_at.is_(None),
        )
        if materia_id is not None:
            stmt = stmt.where(InstanciaEncuentro.materia_id == materia_id)
        if estado is not None:
            stmt = stmt.where(InstanciaEncuentro.estado == estado)
        if fecha_desde is not None:
            stmt = stmt.where(InstanciaEncuentro.fecha >= fecha_desde)
        if fecha_hasta is not None:
            stmt = stmt.where(InstanciaEncuentro.fecha <= fecha_hasta)

        stmt = stmt.order_by(InstanciaEncuentro.fecha.desc())

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()
        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())
        pages = max(1, (total + limit - 1) // limit) if limit > 0 else 1
        return items, total, pages

    async def list_futuras(
        self,
        materia_id: uuid.UUID | None = None,
    ) -> Sequence[InstanciaEncuentro]:
        stmt = select(InstanciaEncuentro).where(
            InstanciaEncuentro.tenant_id == self._tenant_id,
            InstanciaEncuentro.deleted_at.is_(None),
            InstanciaEncuentro.fecha >= func.current_date(),
            InstanciaEncuentro.estado.in_([
                EstadoInstancia.PROGRAMADO,
                EstadoInstancia.REALIZADO,
            ]),
        )
        if materia_id is not None:
            stmt = stmt.where(InstanciaEncuentro.materia_id == materia_id)
        stmt = stmt.order_by(InstanciaEncuentro.fecha.asc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
