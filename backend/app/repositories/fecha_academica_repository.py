import math
import uuid
from collections.abc import Sequence

from sqlalchemy import Date, func, select

from app.models.fecha_academica import FechaAcademica
from app.repositories.base import BaseRepository


class FechaAcademicaRepository(BaseRepository[FechaAcademica]):
    def __init__(self, session, tenant_id):
        super().__init__(session, tenant_id)
        self._model_class = FechaAcademica

    @property
    def _model(self):
        return self._model_class

    async def list_filters(
        self,
        materia_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        tipo: str | None = None,
        fecha_desde: Date | None = None,
        fecha_hasta: Date | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[Sequence[FechaAcademica], int, int]:
        stmt = select(self._model).where(
            self._model.tenant_id == self._tenant_id,
            self._model.deleted_at.is_(None),
        )
        if materia_id is not None:
            stmt = stmt.where(self._model.materia_id == materia_id)
        if cohorte_id is not None:
            stmt = stmt.where(self._model.cohorte_id == cohorte_id)
        if tipo is not None:
            stmt = stmt.where(self._model.tipo == tipo)
        if fecha_desde is not None:
            stmt = stmt.where(self._model.fecha >= fecha_desde)
        if fecha_hasta is not None:
            stmt = stmt.where(self._model.fecha <= fecha_hasta)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        items = result.scalars().all()
        pages = max(1, math.ceil(total / limit)) if limit > 0 else 1
        return items, total, pages
