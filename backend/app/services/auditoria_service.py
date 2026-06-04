import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.comunicacion_repository import ComunicacionRepository
from app.repositories.materia_repository import MateriaRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.auditoria import (
    MetricaAccionesPorDia,
    MetricaComunicaciones,
    MetricaPorDocente,
    MetricaPorMateria,
)


class AuditoriaService:
    def __init__(self, db: AsyncSession, tenant_id: uuid.UUID):
        self._audit_repo = AuditLogRepository(db, tenant_id)
        self._user_repo = UsuarioRepository(db, tenant_id)
        self._materia_repo = MateriaRepository(db, tenant_id)
        self._com_repo = ComunicacionRepository(db, tenant_id)

    async def acciones_por_dia(
        self,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        materia_id: uuid.UUID | None = None,
        materia_ids: list[uuid.UUID] | None = None,
        actor_id: uuid.UUID | None = None,
    ) -> list[MetricaAccionesPorDia]:
        results = await self._audit_repo.count_by_day(
            desde=desde, hasta=hasta, materia_id=materia_id,
            materia_ids=materia_ids, actor_id=actor_id,
        )
        return [MetricaAccionesPorDia(**r) for r in results]

    async def por_docente(
        self,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        materia_id: uuid.UUID | None = None,
        materia_ids: list[uuid.UUID] | None = None,
    ) -> list[MetricaPorDocente]:
        results = await self._audit_repo.count_by_actor(
            desde=desde, hasta=hasta, materia_id=materia_id,
            materia_ids=materia_ids,
        )
        items = []
        for r in results:
            try:
                user = await self._user_repo.get(r["actor_id"])
                nombre = f"{user.nombre or ''} {user.apellido or ''}".strip() or str(user.id)
            except Exception:
                nombre = str(r["actor_id"])
            items.append(MetricaPorDocente(
                docente_id=r["actor_id"],
                docente_nombre=nombre,
                total=r["total"],
                detalle_por_accion=r["detalle_por_accion"],
            ))
        return items

    async def por_materia(
        self,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        actor_id: uuid.UUID | None = None,
        materia_ids: list[uuid.UUID] | None = None,
    ) -> list[MetricaPorMateria]:
        results = await self._audit_repo.count_by_actor_materia(
            desde=desde, hasta=hasta, actor_id=actor_id,
            materia_ids=materia_ids,
        )
        items = []
        for r in results:
            try:
                materia = await self._materia_repo.get(r["materia_id"])
                nombre = materia.nombre
            except Exception:
                nombre = str(r["materia_id"])
            items.append(MetricaPorMateria(
                docente_id=r["actor_id"],
                materia_id=r["materia_id"],
                materia_nombre=nombre,
                total=r["total"],
            ))
        return items

    async def comunicaciones_por_docente(
        self,
        desde: datetime | None = None,
        hasta: datetime | None = None,
    ) -> list[MetricaComunicaciones]:
        results = await self._com_repo.count_by_estado_agrupado_por_docente(
            desde=desde, hasta=hasta,
        )
        return [MetricaComunicaciones(**r) for r in results]
