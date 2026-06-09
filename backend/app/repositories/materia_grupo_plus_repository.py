import uuid
from datetime import date

from sqlalchemy import or_, select

from app.models.materia_grupo_plus import MateriaGrupoPlus
from app.repositories.base import BaseRepository


class MateriaGrupoPlusRepository(BaseRepository[MateriaGrupoPlus]):
    @property
    def _model(self) -> type[MateriaGrupoPlus]:
        return MateriaGrupoPlus

    async def find_vigente(
        self, materia_id: uuid.UUID, periodo: date,
        tenant_id: uuid.UUID | None = None,
    ) -> MateriaGrupoPlus | None:
        tid = tenant_id or self._tenant_id
        stmt = (
            select(MateriaGrupoPlus)
            .where(
                MateriaGrupoPlus.tenant_id == tid,
                MateriaGrupoPlus.materia_id == materia_id,
                MateriaGrupoPlus.deleted_at.is_(None),
                MateriaGrupoPlus.desde <= periodo,
                or_(MateriaGrupoPlus.hasta.is_(None), MateriaGrupoPlus.hasta >= periodo),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def list_all(self) -> list[MateriaGrupoPlus]:
        stmt = (
            select(MateriaGrupoPlus)
            .where(
                MateriaGrupoPlus.tenant_id == self._tenant_id,
                MateriaGrupoPlus.deleted_at.is_(None),
            )
            .order_by(MateriaGrupoPlus.materia_id, MateriaGrupoPlus.desde.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def exists_vigente(
        self, materia_id: uuid.UUID, grupo: str, desde: date,
        hasta: date | None, exclude_id: uuid.UUID | None = None,
    ) -> bool:
        stmt = select(MateriaGrupoPlus).where(
            MateriaGrupoPlus.tenant_id == self._tenant_id,
            MateriaGrupoPlus.materia_id == materia_id,
            MateriaGrupoPlus.grupo == grupo,
            MateriaGrupoPlus.deleted_at.is_(None),
            MateriaGrupoPlus.desde <= (hasta or date(9999, 12, 31)),
            or_(MateriaGrupoPlus.hasta.is_(None), MateriaGrupoPlus.hasta >= desde),
        )
        if exclude_id is not None:
            stmt = stmt.where(MateriaGrupoPlus.id != exclude_id)
        result = await self._session.execute(stmt)
        return result.scalars().first() is not None
