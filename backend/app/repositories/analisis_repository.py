import uuid
from collections.abc import Sequence
from datetime import date

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calificacion import Calificacion
from app.models.entrada_padron import EntradaPadron
from app.models.version_padron import VersionPadron


class AnalisisRepository:
    """Aggregated read-only queries for analysis, ranking, reports and monitors.

    All queries are tenant-scoped.  No write operations.
    """

    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id

    async def list_actividades(self, materia_id: uuid.UUID, cohorte_id: uuid.UUID) -> list[str]:
        """Return distinct actividad_nombre for a materia/cohorte."""
        stmt = (
            select(Calificacion.actividad_nombre)
            .where(
                Calificacion.tenant_id == self._tenant_id,
                Calificacion.materia_id == materia_id,
                Calificacion.cohorte_id == cohorte_id,
                Calificacion.deleted_at.is_(None),
            )
            .distinct()
            .order_by(Calificacion.actividad_nombre)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_alumnos_por_materia_cohorte(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> Sequence[EntradaPadron]:
        vp_subq = (
            select(VersionPadron.id)
            .where(
                VersionPadron.tenant_id == self._tenant_id,
                VersionPadron.materia_id == materia_id,
                VersionPadron.cohorte_id == cohorte_id,
                VersionPadron.activa.is_(True),
            )
            .scalar_subquery()
        )
        stmt = (
            select(EntradaPadron)
            .where(
                EntradaPadron.tenant_id == self._tenant_id,
                EntradaPadron.version_padron_id.in_(vp_subq),
                EntradaPadron.estado == "activo",
                EntradaPadron.deleted_at.is_(None),
            )
            .order_by(EntradaPadron.legajo)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_calificaciones_por_materia_cohorte(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> Sequence[Calificacion]:
        stmt = (
            select(Calificacion)
            .where(
                Calificacion.tenant_id == self._tenant_id,
                Calificacion.materia_id == materia_id,
                Calificacion.cohorte_id == cohorte_id,
                Calificacion.deleted_at.is_(None),
            )
            .order_by(Calificacion.actividad_nombre, Calificacion.entrada_padron_id)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_aprobadas_count_por_alumno(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> list[dict]:
        """Return per-alumno aggregated counts of approved/not-approved/missing."""
        stmt = (
            select(
                Calificacion.entrada_padron_id,
                func.sum(case((Calificacion.aprobado.is_(True), 1), else_=0)).label("aprobadas"),
                func.sum(case((Calificacion.aprobado.is_(False), 1), else_=0)).label("desaprobadas"),
            )
            .where(
                Calificacion.tenant_id == self._tenant_id,
                Calificacion.materia_id == materia_id,
                Calificacion.cohorte_id == cohorte_id,
                Calificacion.deleted_at.is_(None),
            )
            .group_by(Calificacion.entrada_padron_id)
        )
        result = await self._session.execute(stmt)
        rows = []
        for row in result.all():
            rows.append({
                "entrada_padron_id": row.entrada_padron_id,
                "aprobadas": row.aprobadas,
                "desaprobadas": row.desaprobadas,
            })
        return rows

    async def get_total_actividades(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> int:
        stmt = (
            select(func.count(Calificacion.actividad_nombre.distinct()))
            .where(
                Calificacion.tenant_id == self._tenant_id,
                Calificacion.materia_id == materia_id,
                Calificacion.cohorte_id == cohorte_id,
                Calificacion.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_pendientes_sin_calificar(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> list[dict]:
        """Detect entries where finalization exists but no matching calificacion.

        Returns rows with: entrada_padron_id, legajo, nombre_completo, email.
        """
        vp_subq = (
            select(VersionPadron.id)
            .where(
                VersionPadron.tenant_id == self._tenant_id,
                VersionPadron.materia_id == materia_id,
                VersionPadron.cohorte_id == cohorte_id,
                VersionPadron.activa.is_(True),
            )
            .scalar_subquery()
        )
        stmt = (
            select(
                EntradaPadron.id.label("entrada_padron_id"),
                EntradaPadron.legajo,
                EntradaPadron.nombre_completo,
                EntradaPadron.email,
            )
            .where(
                EntradaPadron.tenant_id == self._tenant_id,
                EntradaPadron.version_padron_id.in_(vp_subq),
                EntradaPadron.deleted_at.is_(None),
                EntradaPadron.estado == "activo",
            )
            .order_by(EntradaPadron.legajo)
        )
        result = await self._session.execute(stmt)
        rows = result.all()
        return [
            {
                "entrada_padron_id": row.entrada_padron_id,
                "legajo": row.legajo,
                "nombre_completo": row.nombre_completo,
                "email": row.email,
            }
            for row in rows
        ]
        return rows

    async def get_monitor_data(
        self,
        materia_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        alumno: str | None = None,
        email: str | None = None,
        actividad: str | None = None,
        min_completion: float | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[dict], int]:
        """Return monitor entries with filters, total count, and pagination."""
        base = (
            select(
                EntradaPadron.id.label("entrada_padron_id"),
                EntradaPadron.legajo,
                EntradaPadron.nombre_completo,
                EntradaPadron.email,
            )
            .where(
                EntradaPadron.tenant_id == self._tenant_id,
                EntradaPadron.deleted_at.is_(None),
                EntradaPadron.estado == "activo",
            )
        )

        if materia_id:
            vp_subq = select(VersionPadron.id).where(
                VersionPadron.tenant_id == self._tenant_id,
                VersionPadron.materia_id == materia_id,
                VersionPadron.activa.is_(True),
            )
            base = base.where(EntradaPadron.version_padron_id.in_(vp_subq))
        if alumno:
            base = base.where(EntradaPadron.nombre_completo.ilike(f"%{alumno}%"))
        if email:
            base = base.where(EntradaPadron.email.ilike(f"%{email}%"))

        # Clone for count
        count_stmt = select(func.count()).select_from(base.subquery())
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        paginated = base.offset(offset).limit(limit).order_by(EntradaPadron.legajo)
        result = await self._session.execute(paginated)
        rows = []
        for row in result.all():
            rows.append({
                "entrada_padron_id": row.entrada_padron_id,
                "legajo": row.legajo,
                "nombre_completo": row.nombre_completo,
                "email": row.email,
            })
        return rows, total
