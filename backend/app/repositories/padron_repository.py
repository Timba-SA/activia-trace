import uuid
from collections.abc import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entrada_padron import EntradaPadron
from app.models.version_padron import VersionPadron
from app.repositories.base import BaseRepository


class VersionPadronRepository(BaseRepository[VersionPadron]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id)
        self._model_class = VersionPadron

    @property
    def _model(self) -> type[VersionPadron]:
        return self._model_class

    async def get_active(self, materia_id: uuid.UUID, cohorte_id: uuid.UUID) -> VersionPadron | None:
        stmt = (
            select(self._model)
            .where(
                self._model.tenant_id == self._tenant_id,
                self._model.materia_id == materia_id,
                self._model.cohorte_id == cohorte_id,
                self._model.activa.is_(True),
                self._model.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def deactivate_all_for_materia_cohorte(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> None:
        stmt = (
            update(self._model)
            .where(
                self._model.tenant_id == self._tenant_id,
                self._model.materia_id == materia_id,
                self._model.cohorte_id == cohorte_id,
                self._model.activa.is_(True),
                self._model.deleted_at.is_(None),
            )
            .values(activa=False)
        )
        await self._session.execute(stmt)

    async def list_by_materia_cohorte(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> Sequence[VersionPadron]:
        stmt = (
            select(self._model)
            .where(
                self._model.tenant_id == self._tenant_id,
                self._model.materia_id == materia_id,
                self._model.cohorte_id == cohorte_id,
                self._model.deleted_at.is_(None),
            )
            .order_by(self._model.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()


class EntradaPadronRepository(BaseRepository[EntradaPadron]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id)
        self._model_class = EntradaPadron

    @property
    def _model(self) -> type[EntradaPadron]:
        return self._model_class

    async def bulk_create(self, entries: list[dict]) -> list[EntradaPadron]:
        instances = [self._model(**entry) for entry in entries]
        for inst in instances:
            self._session.add(inst)
        await self._session.flush()
        return instances

    async def list_by_ids(self, ids: list[uuid.UUID]) -> list[EntradaPadron]:
        stmt = (
            select(self._model)
            .where(
                self._model.id.in_(ids),
                self._model.tenant_id == self._tenant_id,
                self._model.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_version(
        self, version_padron_id: uuid.UUID,
    ) -> Sequence[EntradaPadron]:
        stmt = (
            select(self._model)
            .where(
                self._model.tenant_id == self._tenant_id,
                self._model.version_padron_id == version_padron_id,
                self._model.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()
