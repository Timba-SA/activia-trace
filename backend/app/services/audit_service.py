"""AuditService — programmatic logging of audit entries."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.audit_log_repository import AuditLogRepository


class AuditService:
    """Service that creates AuditLog entries via the repository."""

    def __init__(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
    ) -> None:
        self._repo = AuditLogRepository(db, tenant_id)

    async def log(
        self,
        accion: str,
        actor_id: uuid.UUID,
        tenant_id: uuid.UUID,
        materia_id: uuid.UUID | None = None,
        impersonado_id: uuid.UUID | None = None,
        detalle: dict | None = None,
        filas_afectadas: int = 0,
        ip: str | None = None,
        user_agent: str | None = None,
    ):
        return await self._repo.create(
            tenant_id=tenant_id,
            actor_id=actor_id,
            accion=accion,
            materia_id=materia_id,
            impersonado_id=impersonado_id,
            detalle=detalle,
            filas_afectadas=filas_afectadas,
            ip=ip,
            user_agent=user_agent,
        )
