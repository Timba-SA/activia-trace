import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.carrera import Carrera
from app.repositories.base import BaseRepository


class CarreraRepository(BaseRepository[Carrera]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id)

    @property
    def _model(self) -> type[Carrera]:
        return Carrera

    async def get_by_codigo(
        self, codigo: str, include_deleted: bool = False,
    ) -> Carrera | None:
        stmt = select(Carrera).where(
            Carrera.codigo == codigo,
            Carrera.tenant_id == self._tenant_id,
        )
        if not include_deleted:
            stmt = stmt.where(Carrera.deleted_at.is_(None))
        result = await self._session.execute(stmt)
        return result.scalars().first()
