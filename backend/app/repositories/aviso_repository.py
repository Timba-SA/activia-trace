from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.acknowledgment_aviso import AcknowledgmentAviso
from app.models.asignacion import Asignacion
from app.models.aviso import Aviso
from app.repositories.base import BaseRepository


class AvisoRepository(BaseRepository[Aviso]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id)

    @property
    def _model(self) -> type[Aviso]:
        return Aviso

    async def listar(
        self,
        filters: dict[str, Any] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[Sequence[Aviso], int]:
        stmt = self._build_query()
        stmt = stmt.order_by(Aviso.orden.asc(), Aviso.created_at.desc())

        if filters:
            if "alcance" in filters and filters["alcance"] is not None:
                stmt = stmt.where(Aviso.alcance == filters["alcance"])
            if "activo" in filters and filters["activo"] is not None:
                stmt = stmt.where(Aviso.activo == filters["activo"])
            if "vigente" in filters and filters["vigente"]:
                now = datetime.now(timezone.utc)
                stmt = stmt.where(Aviso.inicio_en <= now, Aviso.fin_en >= now)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        items = result.scalars().all()
        return items, total

    async def listar_visibles(
        self,
        usuario_context: dict[str, Any],
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[Aviso], int]:
        now = datetime.now(timezone.utc)
        roles = usuario_context.get("roles", [])
        materia_ids = usuario_context.get("materia_ids", [])
        cohorte_ids = usuario_context.get("cohorte_ids", [])

        stmt = self._build_query()
        stmt = stmt.where(Aviso.activo == True)
        stmt = stmt.where(Aviso.inicio_en <= now, Aviso.fin_en >= now)

        if roles:
            stmt = stmt.where(
                or_(
                    Aviso.alcance != "PorRol",
                    Aviso.rol_destino.in_(roles),
                )
            )

        # Apply materia filter
        if materia_ids:
            stmt = stmt.where(
                or_(
                    Aviso.alcance != "PorMateria",
                    Aviso.materia_id.in_(materia_ids),
                )
            )

        # Apply cohorte filter
        if cohorte_ids:
            stmt = stmt.where(
                or_(
                    Aviso.alcance != "PorCohorte",
                    Aviso.cohorte_id.in_(cohorte_ids),
                )
            )

        stmt = stmt.order_by(Aviso.orden.asc(), Aviso.created_at.desc())

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        items = result.scalars().all()
        return items, total


class AcknowledgmentRepository(BaseRepository[AcknowledgmentAviso]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id)

    @property
    def _model(self) -> type[AcknowledgmentAviso]:
        return AcknowledgmentAviso

    async def create_or_ignore(
        self, aviso_id: uuid.UUID, usuario_id: uuid.UUID
    ) -> AcknowledgmentAviso:
        existing = await self.exists(aviso_id, usuario_id)
        if existing:
            return existing

        instance = self._model(
            tenant_id=self._tenant_id,
            aviso_id=aviso_id,
            usuario_id=usuario_id,
        )
        self._session.add(instance)
        await self._session.flush()
        return instance

    async def count_by_aviso(self, aviso_id: uuid.UUID) -> int:
        stmt = self._build_query()
        stmt = stmt.where(AcknowledgmentAviso.aviso_id == aviso_id)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        result = await self._session.execute(count_stmt)
        return result.scalar_one()

    async def exists(
        self, aviso_id: uuid.UUID, usuario_id: uuid.UUID
    ) -> AcknowledgmentAviso | None:
        stmt = self._build_query()
        stmt = stmt.where(
            AcknowledgmentAviso.aviso_id == aviso_id,
            AcknowledgmentAviso.usuario_id == usuario_id,
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()
