import uuid

from sqlalchemy import func, select

from app.models.liquidacion import Liquidacion
from app.repositories.base import BaseRepository


class LiquidacionRepository(BaseRepository[Liquidacion]):
    @property
    def _model(self) -> type[Liquidacion]:
        return Liquidacion

    async def find_by_filters(
        self,
        cohorte_id: uuid.UUID | None = None,
        periodo: str | None = None,
        usuario_id: uuid.UUID | None = None,
        estado: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Liquidacion], int]:
        stmt = select(Liquidacion).where(
            Liquidacion.tenant_id == self._tenant_id,
            Liquidacion.deleted_at.is_(None),
        )
        if cohorte_id is not None:
            stmt = stmt.where(Liquidacion.cohorte_id == cohorte_id)
        if periodo is not None:
            stmt = stmt.where(Liquidacion.periodo == periodo)
        if usuario_id is not None:
            stmt = stmt.where(Liquidacion.usuario_id == usuario_id)
        if estado is not None:
            stmt = stmt.where(Liquidacion.estado == estado)

        stmt = stmt.order_by(Liquidacion.created_at.desc())

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())
        return items, total

    async def find_historial(
        self,
        cohorte_id: uuid.UUID | None = None,
        periodo: str | None = None,
        usuario_id: uuid.UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Liquidacion], int]:
        return await self.find_by_filters(
            cohorte_id=cohorte_id,
            periodo=periodo,
            usuario_id=usuario_id,
            estado="Cerrada",
            limit=limit,
            offset=offset,
        )

    async def exists_for_periodo(
        self, cohorte_id: uuid.UUID, periodo: str,
    ) -> bool:
        stmt = select(Liquidacion).where(
            Liquidacion.tenant_id == self._tenant_id,
            Liquidacion.deleted_at.is_(None),
            Liquidacion.cohorte_id == cohorte_id,
            Liquidacion.periodo == periodo,
        ).limit(1)
        result = await self._session.execute(stmt)
        return result.scalars().first() is not None

    async def bulk_create(self, entries: list[dict]) -> list[Liquidacion]:
        instances: list[Liquidacion] = []
        for data in entries:
            instance = Liquidacion(**data)
            self._session.add(instance)
            instances.append(instance)
        await self._session.flush()
        return instances
