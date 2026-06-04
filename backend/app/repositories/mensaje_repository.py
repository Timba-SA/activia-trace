import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.mensaje import Mensaje
from app.repositories.base import BaseRepository


class MensajeRepository(BaseRepository[Mensaje]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id)

    @property
    def _model(self) -> type[Mensaje]:
        return Mensaje

    def _build_query(
        self,
        include_deleted: bool = False,
        skip_tenant_scope: bool = False,
    ):
        stmt = select(self._model)
        stmt = self._apply_tenant_scope(stmt, skip=skip_tenant_scope)
        return stmt

    async def _count(self, **filters: tuple) -> int:
        stmt = select(func.count()).select_from(Mensaje)
        stmt = self._apply_tenant_scope(stmt)
        for attr, value in filters.items():
            column = getattr(Mensaje, attr, None)
            if column is not None:
                stmt = stmt.where(column == value)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def list_by_destinatario(
        self,
        destinatario_id: uuid.UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[Sequence[Mensaje], int]:
        total = await self._count(destinatario_id=destinatario_id)
        stmt = self._build_query()
        stmt = stmt.where(Mensaje.destinatario_id == destinatario_id)
        stmt = stmt.order_by(Mensaje.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        items = result.scalars().all()
        return items, total

    async def get_by_id_and_destinatario(
        self,
        id: uuid.UUID,
        destinatario_id: uuid.UUID,
    ) -> Mensaje:
        stmt = self._build_query()
        stmt = stmt.where(
            Mensaje.id == id,
            Mensaje.destinatario_id == destinatario_id,
        )
        result = await self._session.execute(stmt)
        instance = result.scalars().first()
        if instance is None:
            raise NotFoundError(
                f"Mensaje with id={id} not found for this user"
            )
        return instance

    async def create(
        self,
        remitente_id: uuid.UUID,
        destinatario_id: uuid.UUID,
        hilo_id: uuid.UUID | None,
        asunto: str,
        cuerpo: str,
    ) -> Mensaje:
        instance = Mensaje(
            tenant_id=self._tenant_id,
            remitente_id=remitente_id,
            destinatario_id=destinatario_id,
            hilo_id=hilo_id,
            asunto=asunto,
            cuerpo=cuerpo,
            leido=False,
        )
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def list_by_hilo(
        self,
        hilo_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[Sequence[Mensaje], int]:
        total = await self._count(hilo_id=hilo_id)
        stmt = self._build_query()
        stmt = stmt.where(Mensaje.hilo_id == hilo_id)
        stmt = stmt.order_by(Mensaje.created_at.asc())
        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        items = result.scalars().all()
        return items, total

    async def marcar_leido(
        self,
        id: uuid.UUID,
        destinatario_id: uuid.UUID,
    ) -> Mensaje:
        mensaje = await self.get_by_id_and_destinatario(id, destinatario_id)
        mensaje.leido = True
        await self._session.flush()
        await self._session.refresh(mensaje)
        return mensaje
