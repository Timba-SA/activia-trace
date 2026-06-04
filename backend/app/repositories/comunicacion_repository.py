import uuid
from collections.abc import Sequence
from datetime import date, datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comunicacion import Comunicacion
from app.repositories.base import BaseRepository


class ComunicacionRepository(BaseRepository[Comunicacion]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id)
        self._model_class = Comunicacion

    @property
    def _model(self) -> type[Comunicacion]:
        return self._model_class

    async def bulk_create(self, entries: list[dict]) -> list[Comunicacion]:
        instances = [self._model(**entry) for entry in entries]
        for inst in instances:
            self._session.add(inst)
        await self._session.flush()
        return instances

    async def get_estado(self, lote_id: uuid.UUID) -> dict:
        """Return a summary of counts by estado for a given lote_id."""
        stmt = (
            select(
                self._model.estado,
                func.count(self._model.id),
            )
            .where(
                self._model.tenant_id == self._tenant_id,
                self._model.lote_id == lote_id,
                self._model.deleted_at.is_(None),
            )
            .group_by(self._model.estado)
        )
        result = await self._session.execute(stmt)
        counts: dict[str, int] = {"Pendiente": 0, "Enviando": 0, "Enviado": 0, "Error": 0, "Cancelado": 0}
        total = 0
        for estado, count in result.all():
            counts[estado] = count
            total += count
        return {
            "lote_id": str(lote_id),
            "total": total,
            "pendientes": counts["Pendiente"],
            "enviando": counts["Enviando"],
            "enviados": counts["Enviado"],
            "errores": counts["Error"],
            "cancelados": counts["Cancelado"],
        }

    async def get_pendientes(self, limit: int = 50) -> Sequence[Comunicacion]:
        """Get messages ready for worker processing (Pendiente, not requiring approval)."""
        stmt = (
            select(self._model)
            .where(
                self._model.tenant_id == self._tenant_id,
                self._model.estado == "Pendiente",
                self._model.requiere_aprobacion.is_(False),
                self._model.deleted_at.is_(None),
            )
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_pendientes_aprobacion(self, lote_id: uuid.UUID) -> Sequence[Comunicacion]:
        """Get messages pending approval for a specific lote."""
        stmt = (
            select(self._model)
            .where(
                self._model.tenant_id == self._tenant_id,
                self._model.lote_id == lote_id,
                self._model.estado == "Pendiente",
                self._model.requiere_aprobacion.is_(True),
                self._model.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def update_estado(
        self,
        id: uuid.UUID,
        estado: str,
        enviado_at: datetime | None = None,
        error_msg: str | None = None,
    ) -> None:
        values = {"estado": estado}
        if enviado_at is not None:
            values["enviado_at"] = enviado_at
        if error_msg is not None:
            values["error_msg"] = error_msg
        stmt = (
            update(self._model)
            .where(
                self._model.id == id,
                self._model.tenant_id == self._tenant_id,
            )
            .values(**values)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def aprobar_lote(self, lote_id: uuid.UUID) -> int:
        """Approve all pending messages in a lote — transiciona a Enviando."""
        pendientes = await self.get_pendientes_aprobacion(lote_id)
        count = 0
        for msg in pendientes:
            stmt = (
                update(self._model)
                .where(
                    self._model.id == msg.id,
                    self._model.tenant_id == self._tenant_id,
                )
                .values(estado="Enviando")
            )
            await self._session.execute(stmt)
            count += 1
        await self._session.flush()
        return count

    async def cancelar_lote(self, lote_id: uuid.UUID) -> int:
        """Cancel all pending messages in a lote — transiciona a Cancelado."""
        pendientes = await self.get_pendientes_aprobacion(lote_id)
        count = 0
        for msg in pendientes:
            stmt = (
                update(self._model)
                .where(
                    self._model.id == msg.id,
                    self._model.tenant_id == self._tenant_id,
                )
                .values(estado="Cancelado")
            )
            await self._session.execute(stmt)
            count += 1
        await self._session.flush()
        return count

    async def count_by_estado_agrupado_por_docente(
        self,
        desde: datetime | None = None,
        hasta: datetime | None = None,
    ) -> list[dict]:
        stmt = (
            select(
                self._model.enviado_por_id,
                self._model.estado,
                func.count().label("cnt"),
            )
            .where(
                self._model.tenant_id == self._tenant_id,
                self._model.deleted_at.is_(None),
            )
            .group_by(self._model.enviado_por_id, self._model.estado)
        )
        if desde is not None:
            stmt = stmt.where(self._model.created_at >= desde)
        if hasta is not None:
            stmt = stmt.where(self._model.created_at <= hasta)
        result = await self._session.execute(stmt)
        rows = result.all()

        docente_map: dict[uuid.UUID, dict] = {}
        for row in rows:
            if row.enviado_por_id not in docente_map:
                docente_map[row.enviado_por_id] = {
                    "docente_id": row.enviado_por_id,
                    "estados": {},
                }
            docente_map[row.enviado_por_id]["estados"][row.estado] = row.cnt
        return list(docente_map.values())

    async def count_by_lote(self, lote_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(self._model)
            .where(
                self._model.tenant_id == self._tenant_id,
                self._model.lote_id == lote_id,
                self._model.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
