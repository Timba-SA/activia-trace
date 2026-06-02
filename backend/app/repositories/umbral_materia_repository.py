import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.umbral_materia import UmbralMateria
from app.repositories.base import BaseRepository


class UmbralMateriaRepository(BaseRepository[UmbralMateria]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id)
        self._model_class = UmbralMateria

    @property
    def _model(self) -> type[UmbralMateria]:
        return self._model_class

    async def get_by_materia(self, materia_id: uuid.UUID) -> UmbralMateria | None:
        stmt = (
            select(self._model)
            .where(
                self._model.tenant_id == self._tenant_id,
                self._model.materia_id == materia_id,
                self._model.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def upsert(self, materia_id: uuid.UUID, **kwargs) -> UmbralMateria:
        existing = await self.get_by_materia(materia_id)
        if existing is not None:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(existing, key, value)
            await self._session.flush()
            await self._session.refresh(existing)
            return existing
        return await self.create(materia_id=materia_id, **kwargs)
