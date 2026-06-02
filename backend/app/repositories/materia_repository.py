import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.materia import Materia
from app.repositories.base import BaseRepository


class MateriaRepository(BaseRepository[Materia]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id)

    @property
    def _model(self) -> type[Materia]:
        return Materia

    async def get_by_codigo(
        self, codigo: str, include_deleted: bool = False,
    ) -> Materia | None:
        stmt = select(Materia).where(
            Materia.codigo == codigo,
            Materia.tenant_id == self._tenant_id,
        )
        if not include_deleted:
            stmt = stmt.where(Materia.deleted_at.is_(None))
        result = await self._session.execute(stmt)
        return result.scalars().first()
