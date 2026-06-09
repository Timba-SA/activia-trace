import uuid

from sqlalchemy import func, select

from app.models.factura import Factura
from app.repositories.base import BaseRepository


class FacturaRepository(BaseRepository[Factura]):
    @property
    def _model(self) -> type[Factura]:
        return Factura

    async def list_by_filters(
        self,
        periodo: str | None = None,
        usuario_id: uuid.UUID | None = None,
        estado: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Factura], int]:
        stmt = select(Factura).where(
            Factura.tenant_id == self._tenant_id,
            Factura.deleted_at.is_(None),
        )
        if periodo is not None:
            stmt = stmt.where(Factura.periodo == periodo)
        if usuario_id is not None:
            stmt = stmt.where(Factura.usuario_id == usuario_id)
        if estado is not None:
            stmt = stmt.where(Factura.estado == estado)

        stmt = stmt.order_by(Factura.cargada_at.desc())

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())
        return items, total
