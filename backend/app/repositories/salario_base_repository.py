import uuid
from datetime import date

from sqlalchemy import and_, func, or_, select

from app.models.salario_base import SalarioBase
from app.repositories.base import BaseRepository


class SalarioBaseRepository(BaseRepository[SalarioBase]):
    @property
    def _model(self) -> type[SalarioBase]:
        return SalarioBase

    async def find_vigente(
        self, rol: str, periodo: date, tenant_id: uuid.UUID | None = None,
    ) -> SalarioBase | None:
        tid = tenant_id or self._tenant_id
        stmt = (
            select(SalarioBase)
            .where(
                SalarioBase.tenant_id == tid,
                SalarioBase.rol == rol,
                SalarioBase.deleted_at.is_(None),
                SalarioBase.desde <= periodo,
                or_(SalarioBase.hasta.is_(None), SalarioBase.hasta >= periodo),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def exists_overlap(
        self, rol: str, desde: date, hasta: date | None,
        exclude_id: uuid.UUID | None = None,
    ) -> bool:
        stmt = select(SalarioBase).where(
            SalarioBase.tenant_id == self._tenant_id,
            SalarioBase.rol == rol,
            SalarioBase.deleted_at.is_(None),
            SalarioBase.desde <= (hasta or date.max),
            or_(SalarioBase.hasta.is_(None), SalarioBase.hasta >= desde),
        )
        if exclude_id is not None:
            stmt = stmt.where(SalarioBase.id != exclude_id)
        result = await self._session.execute(stmt)
        return result.scalars().first() is not None

    async def list_all(self) -> list[SalarioBase]:
        stmt = (
            select(SalarioBase)
            .where(
                SalarioBase.tenant_id == self._tenant_id,
                SalarioBase.deleted_at.is_(None),
            )
            .order_by(SalarioBase.rol, SalarioBase.desde.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
