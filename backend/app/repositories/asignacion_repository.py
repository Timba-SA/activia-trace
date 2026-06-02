import uuid

from sqlalchemy import select
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
