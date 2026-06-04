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

    async def update(self, *args, **kwargs):
        raise NotImplementedError("AuditLog is append-only: update is not permitted")

    async def soft_delete(self, *args, **kwargs):
        raise NotImplementedError("AuditLog is append-only: delete is not permitted")
