import uuid
from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crypto import encrypt
from app.core.exceptions import NotFoundError
from app.models.comunicacion import Comunicacion
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.repositories.comunicacion_repository import ComunicacionRepository
from app.repositories.materia_repository import MateriaRepository
from app.repositories.padron_repository import EntradaPadronRepository
from app.repositories.tenant import TenantRepository
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
        self._tenant_id = tenant_id
        self._current_user_id = current_user_id
        self._padron_repo = EntradaPadronRepository(db, tenant_id)
        self._materia_repo = MateriaRepository(db, tenant_id)
        self._tenant_repo = TenantRepository(db)

    async def _get_entradas(
        self, entrada_ids: list[uuid.UUID], materia_id: uuid.UUID,
    ) -> list[EntradaPadron]:
        entradas = await self._padron_repo.list_by_ids(entrada_ids)
        if not entradas:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No se encontraron destinatarios para esta materia",
            )
        return entradas

    async def _get_materia(self, materia_id: uuid.UUID) -> Materia:
        try:
            return await self._materia_repo.get(materia_id)
        except NotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Materia no encontrada")

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
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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
        try:
            tenant = await self._tenant_repo.get(self._tenant_id)
            value = tenant.aprobacion_comunicaciones_requerida
            return bool(value) if value is not None else False
        except NotFoundError:
            return False

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
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lote no encontrado")
        return EstadoResponse(**result)

    async def aprobar_lote(self, lote_id: uuid.UUID) -> AprobarResponse:
        count = await self._repo.count_by_lote(lote_id)
        if count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lote no encontrado")
        total = await self._repo.aprobar_lote(lote_id)
        return AprobarResponse(lote_id=str(lote_id), total_aprobados=total)

    async def cancelar_lote(self, lote_id: uuid.UUID) -> CancelarResponse:
        count = await self._repo.count_by_lote(lote_id)
        if count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lote no encontrado")
        total = await self._repo.cancelar_lote(lote_id)
        return CancelarResponse(lote_id=str(lote_id), total_cancelados=total)
