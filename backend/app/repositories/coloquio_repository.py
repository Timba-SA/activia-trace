from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.convocatoria_alumno import ConvocatoriaAlumno
from app.models.evaluacion import Evaluacion
from app.models.reserva_evaluacion import EstadoReserva, ReservaEvaluacion
from app.models.resultado_evaluacion import ResultadoEvaluacion
from app.models.turno_disponible import TurnoDisponible
from app.repositories.base import BaseRepository


class EvaluacionRepository(BaseRepository[Evaluacion]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id)

    @property
    def _model(self) -> type[Evaluacion]:
        return Evaluacion

    async def list_with_indicators(
        self,
        limit: int = 20,
        offset: int = 0,
        materia_id: uuid.UUID | None = None,
    ) -> tuple[Sequence[Evaluacion], int, int]:
        stmt = self._build_query()
        if materia_id is not None:
            stmt = stmt.where(Evaluacion.materia_id == materia_id)
        stmt = stmt.order_by(Evaluacion.created_at.desc())

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        items = result.scalars().all()
        pages = max(1, (total + limit - 1) // limit) if limit > 0 else 1
        return items, total, pages


class TurnoDisponibleRepository(BaseRepository[TurnoDisponible]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id)

    @property
    def _model(self) -> type[TurnoDisponible]:
        return TurnoDisponible

    async def list_by_evaluacion(
        self, evaluacion_id: uuid.UUID
    ) -> Sequence[TurnoDisponible]:
        stmt = self._build_query()
        stmt = stmt.where(TurnoDisponible.evaluacion_id == evaluacion_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def decrementar_cupo(self, turno_id: uuid.UUID) -> int:
        stmt = (
            update(TurnoDisponible)
            .where(TurnoDisponible.id == turno_id)
            .where(TurnoDisponible.cupos_restantes > 0)
            .values(cupos_restantes=TurnoDisponible.cupos_restantes - 1)
        )
        result = await self._session.execute(stmt)
        return result.rowcount

    async def reincrementar_cupo(self, turno_id: uuid.UUID) -> None:
        stmt = (
            update(TurnoDisponible)
            .where(TurnoDisponible.id == turno_id)
            .values(cupos_restantes=TurnoDisponible.cupos_restantes + 1)
        )
        await self._session.execute(stmt)

    async def delete_by_evaluacion(self, evaluacion_id: uuid.UUID) -> None:
        stmt = (
            update(TurnoDisponible)
            .where(TurnoDisponible.evaluacion_id == evaluacion_id)
            .where(TurnoDisponible.deleted_at.is_(None))
            .values(deleted_at=func.now())
        )
        await self._session.execute(stmt)


class ReservaEvaluacionRepository(BaseRepository[ReservaEvaluacion]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id)

    @property
    def _model(self) -> type[ReservaEvaluacion]:
        return ReservaEvaluacion

    async def has_activa_en_evaluacion(
        self, evaluacion_id: uuid.UUID, alumno_id: uuid.UUID
    ) -> bool:
        stmt = (
            select(ReservaEvaluacion)
            .where(ReservaEvaluacion.tenant_id == self._tenant_id)
            .where(ReservaEvaluacion.evaluacion_id == evaluacion_id)
            .where(ReservaEvaluacion.alumno_id == alumno_id)
            .where(ReservaEvaluacion.estado == EstadoReserva.ACTIVA)
            .where(ReservaEvaluacion.deleted_at.is_(None))
        )
        result = await self._session.execute(stmt)
        return result.scalars().first() is not None

    async def count_activas(self) -> int:
        stmt = (
            select(func.count())
            .select_from(ReservaEvaluacion)
            .where(
                ReservaEvaluacion.tenant_id == self._tenant_id,
                ReservaEvaluacion.estado == EstadoReserva.ACTIVA,
                ReservaEvaluacion.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def cancelar(self, reserva_id: uuid.UUID) -> ReservaEvaluacion:
        stmt = (
            update(ReservaEvaluacion)
            .where(ReservaEvaluacion.id == reserva_id)
            .where(ReservaEvaluacion.tenant_id == self._tenant_id)
            .where(ReservaEvaluacion.deleted_at.is_(None))
            .values(
                estado=EstadoReserva.CANCELADA,
                deleted_at=func.now(),
            )
        )
        result = await self._session.execute(stmt)
        if result.rowcount == 0:
            raise NotFoundError(f"ReservaEvaluacion with id={reserva_id} not found")
        return await self.get(reserva_id, include_deleted=True)


class ResultadoEvaluacionRepository(BaseRepository[ResultadoEvaluacion]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id)

    @property
    def _model(self) -> type[ResultadoEvaluacion]:
        return ResultadoEvaluacion

    async def list_by_evaluacion(
        self, evaluacion_id: uuid.UUID
    ) -> Sequence[ResultadoEvaluacion]:
        stmt = self._build_query()
        stmt = stmt.where(ResultadoEvaluacion.evaluacion_id == evaluacion_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create_batch(
        self, items: list[dict]
    ) -> list[ResultadoEvaluacion]:
        instances = []
        for item in items:
            instance = self._model(**item)
            self._session.add(instance)
            instances.append(instance)
        await self._session.flush()
        return instances


class ConvocatoriaAlumnoRepository(BaseRepository[ConvocatoriaAlumno]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id)

    @property
    def _model(self) -> type[ConvocatoriaAlumno]:
        return ConvocatoriaAlumno

    async def upsert(self, evaluacion_id: uuid.UUID, alumno_id: uuid.UUID) -> ConvocatoriaAlumno:
        stmt = (
            select(ConvocatoriaAlumno)
            .where(ConvocatoriaAlumno.tenant_id == self._tenant_id)
            .where(ConvocatoriaAlumno.evaluacion_id == evaluacion_id)
            .where(ConvocatoriaAlumno.alumno_id == alumno_id)
        )
        result = await self._session.execute(stmt)
        existing = result.scalars().first()
        if existing:
            if existing.deleted_at is not None:
                existing.deleted_at = None
                await self._session.flush()
                await self._session.refresh(existing)
            return existing

        instance = self._model(
            tenant_id=self._tenant_id,
            evaluacion_id=evaluacion_id,
            alumno_id=alumno_id,
        )
        self._session.add(instance)
        await self._session.flush()
        return instance

    async def find_by_evaluacion_alumno(
        self, evaluacion_id: uuid.UUID, alumno_id: uuid.UUID
    ) -> ConvocatoriaAlumno | None:
        stmt = self._build_query()
        stmt = stmt.where(
            ConvocatoriaAlumno.evaluacion_id == evaluacion_id,
            ConvocatoriaAlumno.alumno_id == alumno_id,
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def list_by_evaluacion(
        self, evaluacion_id: uuid.UUID
    ) -> Sequence[ConvocatoriaAlumno]:
        stmt = self._build_query()
        stmt = stmt.where(ConvocatoriaAlumno.evaluacion_id == evaluacion_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()
