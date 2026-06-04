import uuid
from collections.abc import Sequence

from sqlalchemy import func, or_, select

from app.models.comentario_tarea import ComentarioTarea
from app.models.tarea import Tarea
from app.repositories.base import BaseRepository


class TareaRepository(BaseRepository[Tarea]):
    def __init__(self, session, tenant_id):
        super().__init__(session, tenant_id)
        self._model_class = Tarea

    @property
    def _model(self) -> type[Tarea]:
        return self._model_class

    async def listar_mis_tareas(
        self,
        usuario_id: uuid.UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[Sequence[Tarea], int]:
        stmt = (
            select(self._model)
            .where(
                self._model.tenant_id == self._tenant_id,
                self._model.asignado_a == usuario_id,
                self._model.deleted_at.is_(None),
            )
            .order_by(self._model.created_at.desc())
        )
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()
        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        items = result.scalars().all()
        return items, total

    async def listar_admin(
        self,
        filtros: dict | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[Sequence[Tarea], int]:
        stmt = (
            select(self._model)
            .where(
                self._model.tenant_id == self._tenant_id,
                self._model.deleted_at.is_(None),
            )
        )

        if filtros:
            if filtros.get("asignado_a"):
                stmt = stmt.where(self._model.asignado_a == filtros["asignado_a"])
            if filtros.get("asignado_por"):
                stmt = stmt.where(self._model.asignado_por == filtros["asignado_por"])
            if filtros.get("materia_id"):
                stmt = stmt.where(self._model.materia_id == filtros["materia_id"])
            if filtros.get("estado"):
                stmt = stmt.where(self._model.estado == filtros["estado"])
            if filtros.get("q"):
                stmt = stmt.where(
                    self._model.descripcion.ilike(f"%{filtros['q']}%")
                )

        stmt = stmt.order_by(self._model.created_at.desc())
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()
        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        items = result.scalars().all()
        return items, total


class ComentarioTareaRepository(BaseRepository[ComentarioTarea]):
    def __init__(self, session, tenant_id):
        super().__init__(session, tenant_id)
        self._model_class = ComentarioTarea

    @property
    def _model(self) -> type[ComentarioTarea]:
        return self._model_class

    async def crear_comentario(
        self, tarea_id: uuid.UUID, autor_id: uuid.UUID, texto: str
    ) -> ComentarioTarea:
        return await self.create(
            tenant_id=self._tenant_id,
            tarea_id=tarea_id,
            autor_id=autor_id,
            texto=texto,
        )

    async def listar_por_tarea(
        self,
        tarea_id: uuid.UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[Sequence[ComentarioTarea], int]:
        stmt = (
            select(self._model)
            .where(
                self._model.tenant_id == self._tenant_id,
                self._model.tarea_id == tarea_id,
                self._model.deleted_at.is_(None),
            )
            .order_by(self._model.creado_at.asc())
        )
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()
        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        items = result.scalars().all()
        return items, total
