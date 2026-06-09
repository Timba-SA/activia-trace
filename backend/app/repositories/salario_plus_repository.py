import uuid
from datetime import date

from sqlalchemy import or_, select

from app.models.salario_plus import SalarioPlus
from app.repositories.base import BaseRepository


class SalarioPlusRepository(BaseRepository[SalarioPlus]):
    @property
    def _model(self) -> type[SalarioPlus]:
        return SalarioPlus

    async def find_vigente(
        self, grupo: str, rol: str, periodo: date,
        tenant_id: uuid.UUID | None = None,
    ) -> SalarioPlus | None:
        tid = tenant_id or self._tenant_id
        stmt = (
            select(SalarioPlus)
            .where(
                SalarioPlus.tenant_id == tid,
                SalarioPlus.grupo == grupo,
                SalarioPlus.rol == rol,
                SalarioPlus.deleted_at.is_(None),
                SalarioPlus.desde <= periodo,
                or_(SalarioPlus.hasta.is_(None), SalarioPlus.hasta >= periodo),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def list_all(self) -> list[SalarioPlus]:
        stmt = (
            select(SalarioPlus)
            .where(
                SalarioPlus.tenant_id == self._tenant_id,
                SalarioPlus.deleted_at.is_(None),
            )
            .order_by(SalarioPlus.grupo, SalarioPlus.rol)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
