import math
import uuid
from collections.abc import Sequence

from sqlalchemy import func, select, update

from app.models.programa_materia import ProgramaMateria
from app.repositories.base import BaseRepository


class ProgramaMateriaRepository(BaseRepository[ProgramaMateria]):
    def __init__(self, session, tenant_id):
        super().__init__(session, tenant_id)
        self._model_class = ProgramaMateria

    @property
    def _model(self):
        return self._model_class

    async def list_filters(
        self,
        materia_id: uuid.UUID | None = None,
        carrera_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        activo: bool | None = None,
        incluir_inactivos: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[Sequence[ProgramaMateria], int, int]:
        stmt = select(self._model).where(
            self._model.tenant_id == self._tenant_id,
            self._model.deleted_at.is_(None),
        )
        if materia_id is not None:
            stmt = stmt.where(self._model.materia_id == materia_id)
        if carrera_id is not None:
            stmt = stmt.where(self._model.carrera_id == carrera_id)
        if cohorte_id is not None:
            stmt = stmt.where(self._model.cohorte_id == cohorte_id)
        if not incluir_inactivos:
            stmt = stmt.where(self._model.activo.is_(True))
        elif activo is not None:
            stmt = stmt.where(self._model.activo.is_(activo))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        items = result.scalars().all()
        pages = max(1, math.ceil(total / limit)) if limit > 0 else 1
        return items, total, pages

    async def get_active_for_materia_carrera_cohorte(
        self,
        materia_id: uuid.UUID,
        carrera_id: uuid.UUID,
        cohorte_id: uuid.UUID | None = None,
    ) -> ProgramaMateria | None:
        stmt = (
            select(self._model)
            .where(
                self._model.tenant_id == self._tenant_id,
                self._model.materia_id == materia_id,
                self._model.carrera_id == carrera_id,
                self._model.cohorte_id == cohorte_id,
                self._model.activo.is_(True),
                self._model.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def get_max_version(
        self,
        materia_id: uuid.UUID,
        carrera_id: uuid.UUID,
        cohorte_id: uuid.UUID | None = None,
    ) -> int:
        stmt = (
            select(func.coalesce(func.max(self._model.version), 0))
            .where(
                self._model.tenant_id == self._tenant_id,
                self._model.materia_id == materia_id,
                self._model.carrera_id == carrera_id,
                self._model.cohorte_id == cohorte_id,
                self._model.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def deactivate_all_for(
        self,
        materia_id: uuid.UUID,
        carrera_id: uuid.UUID,
        cohorte_id: uuid.UUID | None = None,
    ) -> None:
        stmt = (
            update(self._model)
            .where(
                self._model.tenant_id == self._tenant_id,
                self._model.materia_id == materia_id,
                self._model.carrera_id == carrera_id,
                self._model.cohorte_id == cohorte_id,
                self._model.activo.is_(True),
                self._model.deleted_at.is_(None),
            )
            .values(activo=False)
        )
        await self._session.execute(stmt)
        await self._session.flush()
