import uuid
from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crypto import encrypt
from app.models.comunicacion import Comunicacion
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.repositories.comunicacion_repository import ComunicacionRepository
from app.schemas.comunicacion import (
    AprobarResponse,
    CancelarResponse,
    EnvioResponse,
    EstadoResponse,
    PreviewResponse,
)


def render_template(template: str, **kwargs: str) -> str:
    """Replace {variable} placeholders with actual values.

    Unknown variables are left as-is (no error).
    """
    result = template
    for key, value in kwargs.items():
        placeholder = "{" + key + "}"
        result = result.replace(placeholder, value)
    return result


class ComunicacionService:
    def __init__(self, db: AsyncSession, tenant_id: uuid.UUID, current_user_id: uuid.UUID) -> None:
        self._repo = ComunicacionRepository(db, tenant_id)
        self._db = db
        self._tenant_id = tenant_id
        self._current_user_id = current_user_id

    async def _get_entradas(
        self, entrada_ids: list[uuid.UUID], materia_id: uuid.UUID,
    ) -> Sequence[EntradaPadron]:
        """Fetch and validate EntradaPadron records."""
        from sqlalchemy import select
        stmt = (
            select(EntradaPadron)
            .where(
                EntradaPadron.id.in_(entrada_ids),
                EntradaPadron.tenant_id == self._tenant_id,
                EntradaPadron.deleted_at.is_(None),
            )
        )
        result = await self._db.execute(stmt)
        entradas = result.scalars().all()

        if not entradas:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="No se encontraron destinatarios para esta materia",
            )
        return entradas

    async def _get_materia(self, materia_id: uuid.UUID) -> Materia:
        from sqlalchemy import select
        stmt = select(Materia).where(
            Materia.id == materia_id,
            Materia.tenant_id == self._tenant_id,
            Materia.deleted_at.is_(None),
        )
        result = await self._db.execute(stmt)
        materia = result.scalars().first()
        if materia is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Materia no encontrada",
            )
        return materia

    async def preview(
        self,
        materia_id: uuid.UUID,
        cohorte_id: uuid.UUID | None,
        destinatario_entrada_ids: list[uuid.UUID],
        asunto_template: str,
        cuerpo_template: str,
    ) -> PreviewResponse:
        if not destinatario_entrada_ids:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="No hay destinatarios para esta materia",
            )

        materia = await self._get_materia(materia_id)
        entradas = await self._get_entradas(destinatario_entrada_ids, materia_id)

        primera = entradas[0]
        asunto_renderizado = render_template(
            asunto_template,
            alumno=primera.nombre_completo,
            materia=materia.nombre,
            legajo=primera.legajo,
        )
        cuerpo_renderizado = render_template(
            cuerpo_template,
            alumno=primera.nombre_completo,
            materia=materia.nombre,
            legajo=primera.legajo,
        )

        return PreviewResponse(
            asunto_renderizado=asunto_renderizado,
            cuerpo_renderizado=cuerpo_renderizado,
            alumno_nombre=primera.nombre_completo,
        )

    async def _get_aprobacion_requerida(self) -> bool:
        """Check tenant-level config for aprobacion_requerida.

        Reads the `aprobacion_comunicaciones_requerida` column from the tenant table.
        Defaults to False.
        """
        from sqlalchemy import select as sa_select
        from app.models.tenant import Tenant
        tenant_stmt = sa_select(Tenant.aprobacion_comunicaciones_requerida).where(
            Tenant.id == self._tenant_id
        )
        result = await self._db.execute(tenant_stmt)
        row = result.one_or_none()
        if row is None:
            return False
        return bool(row[0]) if row[0] is not None else False

    async def enviar(
        self,
        materia_id: uuid.UUID,
        cohorte_id: uuid.UUID | None,
        destinatario_entrada_ids: list[uuid.UUID],
        asunto: str,
        cuerpo: str,
    ) -> EnvioResponse:
        if not destinatario_entrada_ids:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="No hay destinatarios para enviar",
            )

        materia = await self._get_materia(materia_id)
        entradas = await self._get_entradas(destinatario_entrada_ids, materia_id)

        requiere_aprobacion = await self._get_aprobacion_requerida()
        lote_id = uuid.uuid4()

        records = []
        for ep in entradas:
            asunto_renderizado = render_template(
                asunto,
                alumno=ep.nombre_completo,
                materia=materia.nombre,
                legajo=ep.legajo,
            )
            cuerpo_renderizado = render_template(
                cuerpo,
                alumno=ep.nombre_completo,
                materia=materia.nombre,
                legajo=ep.legajo,
            )
            destinatario_cifrado = encrypt(ep.email)
            records.append({
                "tenant_id": self._tenant_id,
                "enviado_por_id": self._current_user_id,
                "materia_id": materia_id,
                "cohorte_id": cohorte_id,
                "lote_id": lote_id,
                "destinatario": destinatario_cifrado,
                "asunto": asunto_renderizado,
                "cuerpo": cuerpo_renderizado,
                "estado": "Pendiente",
                "requiere_aprobacion": requiere_aprobacion,
            })

        await self._repo.bulk_create(records)

        estado = "aprobacion_pendiente" if requiere_aprobacion else "encolado"
        return EnvioResponse(
            lote_id=str(lote_id),
            total=len(records),
            estado=estado,
        )

    async def get_estado(self, lote_id: uuid.UUID) -> EstadoResponse:
        result = await self._repo.get_estado(lote_id)
        if result["total"] == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lote no encontrado",
            )
        return EstadoResponse(**result)

    async def aprobar_lote(self, lote_id: uuid.UUID) -> AprobarResponse:
        count = await self._repo.count_by_lote(lote_id)
        if count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lote no encontrado",
            )
        total = await self._repo.aprobar_lote(lote_id)
        return AprobarResponse(
            lote_id=str(lote_id),
            total_aprobados=total,
        )

    async def cancelar_lote(self, lote_id: uuid.UUID) -> CancelarResponse:
        count = await self._repo.count_by_lote(lote_id)
        if count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lote no encontrado",
            )
        total = await self._repo.cancelar_lote(lote_id)
        return CancelarResponse(
            lote_id=str(lote_id),
            total_cancelados=total,
        )
