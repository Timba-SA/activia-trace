import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cohorte import Cohorte
from app.repositories.base import BaseRepository


class CohorteRepository(BaseRepository[Cohorte]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id)

    @property
    def _model(self) -> type[Cohorte]:
        return Cohorte

    async def get_by_nombre_and_carrera(
        self, nombre: str, carrera_id: uuid.UUID, include_deleted: bool = False,
    ) -> Cohorte | None:
        stmt = select(Cohorte).where(
            Cohorte.nombre == nombre,
            Cohorte.carrera_id == carrera_id,
            Cohorte.tenant_id == self._tenant_id,
        )
        if not include_deleted:
            stmt = stmt.where(Cohorte.deleted_at.is_(None))
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def count_by_carrera(
        self, carrera_id: uuid.UUID, include_deleted: bool = False,
    ) -> int:
        stmt = select(func.count()).select_from(Cohorte).where(
            Cohorte.carrera_id == carrera_id,
            Cohorte.tenant_id == self._tenant_id,
        )
        if not include_deleted:
            stmt = stmt.where(Cohorte.deleted_at.is_(None))
        result = await self._session.execute(stmt)
        return result.scalar_one()
