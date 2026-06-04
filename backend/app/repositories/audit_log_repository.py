import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select

from app.core.exceptions import NotFoundError
from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    @property
    def _model(self) -> type[AuditLog]:
        return AuditLog

    async def create(self, **kwargs) -> AuditLog:
        instance = self._model(**kwargs)
        self._session.add(instance)
        await self._session.flush()
        return instance

    async def find(
        self,
        limit: int = 20,
        offset: int = 0,
        accion: str | None = None,
        actor_id: uuid.UUID | None = None,
        materia_id: uuid.UUID | None = None,
        materia_ids: list[uuid.UUID] | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
    ) -> tuple[Sequence[AuditLog], int, int]:
        stmt = select(self._model)
        stmt = self._apply_tenant_scope(stmt)

        if accion is not None:
            stmt = stmt.where(self._model.accion == accion)
        if actor_id is not None:
            stmt = stmt.where(self._model.actor_id == actor_id)
        if materia_id is not None:
            stmt = stmt.where(self._model.materia_id == materia_id)
        if materia_ids is not None:
            stmt = stmt.where(self._model.materia_id.in_(materia_ids))
        if desde is not None:
            stmt = stmt.where(self._model.fecha_hora >= desde)
        if hasta is not None:
            stmt = stmt.where(self._model.fecha_hora <= hasta)

        stmt = stmt.order_by(self._model.fecha_hora.desc())

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        items = result.scalars().all()

        import math
        pages = max(1, math.ceil(total / limit)) if limit > 0 else 1
        return items, total, pages

    async def count_by_day(
        self,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        materia_id: uuid.UUID | None = None,
        materia_ids: list[uuid.UUID] | None = None,
        actor_id: uuid.UUID | None = None,
    ) -> list[dict]:
        stmt = select(
            func.date(self._model.fecha_hora).label("fecha"),
            func.count().label("cantidad"),
        )
        stmt = self._apply_tenant_scope(stmt)
        if desde is not None:
            stmt = stmt.where(self._model.fecha_hora >= desde)
        if hasta is not None:
            stmt = stmt.where(self._model.fecha_hora <= hasta)
        if materia_id is not None:
            stmt = stmt.where(self._model.materia_id == materia_id)
        if materia_ids is not None:
            stmt = stmt.where(self._model.materia_id.in_(materia_ids))
        if actor_id is not None:
            stmt = stmt.where(self._model.actor_id == actor_id)
        stmt = stmt.group_by(func.date(self._model.fecha_hora))
        stmt = stmt.order_by(func.date(self._model.fecha_hora))
        result = await self._session.execute(stmt)
        return [
            {"fecha": row.fecha, "cantidad": row.cantidad}
            for row in result.all()
        ]

    async def count_by_actor(
        self,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        materia_id: uuid.UUID | None = None,
        materia_ids: list[uuid.UUID] | None = None,
    ) -> list[dict]:
        stmt = select(
            self._model.actor_id,
            self._model.accion,
            func.count().label("cnt"),
        )
        stmt = self._apply_tenant_scope(stmt)
        if desde is not None:
            stmt = stmt.where(self._model.fecha_hora >= desde)
        if hasta is not None:
            stmt = stmt.where(self._model.fecha_hora <= hasta)
        if materia_id is not None:
            stmt = stmt.where(self._model.materia_id == materia_id)
        if materia_ids is not None:
            stmt = stmt.where(self._model.materia_id.in_(materia_ids))
        stmt = stmt.group_by(self._model.actor_id, self._model.accion)
        result = await self._session.execute(stmt)
        rows = result.all()

        actor_map: dict[uuid.UUID, dict] = {}
        for row in rows:
            if row.actor_id not in actor_map:
                actor_map[row.actor_id] = {
                    "actor_id": row.actor_id,
                    "total": 0,
                    "detalle_por_accion": {},
                }
            actor_map[row.actor_id]["total"] += row.cnt
            actor_map[row.actor_id]["detalle_por_accion"][row.accion] = row.cnt
        return list(actor_map.values())

    async def count_by_actor_materia(
        self,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        actor_id: uuid.UUID | None = None,
        materia_ids: list[uuid.UUID] | None = None,
    ) -> list[dict]:
        stmt = select(
            self._model.actor_id,
            self._model.materia_id,
            func.count().label("total"),
        )
        stmt = self._apply_tenant_scope(stmt)
        if desde is not None:
            stmt = stmt.where(self._model.fecha_hora >= desde)
        if hasta is not None:
            stmt = stmt.where(self._model.fecha_hora <= hasta)
        if actor_id is not None:
            stmt = stmt.where(self._model.actor_id == actor_id)
        if materia_ids is not None:
            stmt = stmt.where(self._model.materia_id.in_(materia_ids))
        stmt = stmt.group_by(self._model.actor_id, self._model.materia_id)
        stmt = stmt.order_by(func.count().desc())
        result = await self._session.execute(stmt)
        return [
            {"actor_id": row.actor_id, "materia_id": row.materia_id, "total": row.total}
            for row in result.all()
        ]

    async def update(self, *args, **kwargs):
        raise NotImplementedError("AuditLog is append-only: update is not permitted")

    async def soft_delete(self, *args, **kwargs):
        raise NotImplementedError("AuditLog is append-only: delete is not permitted")
