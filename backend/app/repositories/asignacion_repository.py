from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asignacion import Asignacion
from app.repositories.base import BaseRepository


class AsignacionRepository(BaseRepository[Asignacion]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id)

    @property
    def _model(self) -> type[Asignacion]:
        return Asignacion

    async def list_by_usuario(self, usuario_id: uuid.UUID) -> list[Asignacion]:
        stmt = select(Asignacion).where(
            Asignacion.usuario_id == usuario_id,
            Asignacion.tenant_id == self._tenant_id,
            Asignacion.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_with_filters(
        self,
        filters: dict,
        usuario_id: uuid.UUID | None = None,
        tenant_id: uuid.UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Asignacion], int, int]:
        stmt = select(Asignacion).where(
            Asignacion.tenant_id == (tenant_id or self._tenant_id),
            Asignacion.deleted_at.is_(None),
        )
        if usuario_id is not None:
            stmt = stmt.where(Asignacion.usuario_id == usuario_id)
        if "materia_id" in filters and filters["materia_id"] is not None:
            stmt = stmt.where(Asignacion.materia_id == filters["materia_id"])
        if "carrera_id" in filters and filters["carrera_id"] is not None:
            stmt = stmt.where(Asignacion.carrera_id == filters["carrera_id"])
        if "cohorte_id" in filters and filters["cohorte_id"] is not None:
            stmt = stmt.where(Asignacion.cohorte_id == filters["cohorte_id"])
        if "rol" in filters and filters["rol"] is not None:
            stmt = stmt.where(Asignacion.rol == filters["rol"])
        if "responsable_id" in filters and filters["responsable_id"] is not None:
            stmt = stmt.where(Asignacion.responsable_id == filters["responsable_id"])
        if "estado" in filters and filters["estado"] is not None:
            today = func.current_date()
            if filters["estado"] == "vigente":
                stmt = stmt.where(
                    and_(
                        Asignacion.fecha_inicio <= today,
                        or_(Asignacion.fecha_fin >= today, Asignacion.fecha_fin.is_(None)),
                    )
                )
            elif filters["estado"] == "vencida":
                stmt = stmt.where(Asignacion.fecha_fin < today)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()
        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())
        pages = max(1, (total + limit - 1) // limit) if limit > 0 else 1
        return items, total, pages

    async def bulk_create(self, entries: list[dict]) -> list[Asignacion]:
        instances: list[Asignacion] = []
        for data in entries:
            instance = Asignacion(**data)
            self._session.add(instance)
            instances.append(instance)
        await self._session.flush()
        return instances

    async def list_by_team_scope(
        self,
        materia_id: uuid.UUID,
        carrera_id: uuid.UUID,
        cohorte_id: uuid.UUID,
        tenant_id: uuid.UUID | None = None,
    ) -> list[Asignacion]:
        stmt = select(Asignacion).where(
            Asignacion.tenant_id == (tenant_id or self._tenant_id),
            Asignacion.deleted_at.is_(None),
            Asignacion.materia_id == materia_id,
            Asignacion.carrera_id == carrera_id,
            Asignacion.cohorte_id == cohorte_id,
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_vigencia_by_team(
        self,
        materia_id: uuid.UUID,
        carrera_id: uuid.UUID,
        cohorte_id: uuid.UUID,
        fecha_inicio: date,
        fecha_fin: date,
        tenant_id: uuid.UUID | None = None,
    ) -> int:
        tid = tenant_id or self._tenant_id
        stmt = (
            update(Asignacion)
            .where(
                Asignacion.tenant_id == tid,
                Asignacion.deleted_at.is_(None),
                Asignacion.materia_id == materia_id,
                Asignacion.carrera_id == carrera_id,
                Asignacion.cohorte_id == cohorte_id,
            )
            .values(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount
