import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calificacion import Calificacion
from app.repositories.base import BaseRepository


class CalificacionRepository(BaseRepository[Calificacion]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id)
        self._model_class = Calificacion

    @property
    def _model(self) -> type[Calificacion]:
        return self._model_class

    async def list_by_materia_cohorte(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> Sequence[Calificacion]:
        stmt = (
            select(self._model)
            .where(
                self._model.tenant_id == self._tenant_id,
                self._model.materia_id == materia_id,
                self._model.cohorte_id == cohorte_id,
                self._model.deleted_at.is_(None),
            )
            .order_by(self._model.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def bulk_create(self, entries: list[dict]) -> list[Calificacion]:
        instances = [self._model(**entry) for entry in entries]
        for inst in instances:
            self._session.add(inst)
        await self._session.flush()
        return instances
