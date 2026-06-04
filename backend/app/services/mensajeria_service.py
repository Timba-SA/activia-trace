import uuid
from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.mensaje import Mensaje
from app.repositories.auth_repository import UsuarioRepository
from app.repositories.mensaje_repository import MensajeRepository
from app.schemas.mensaje import MensajeCreate, MensajeOut, MensajeResponder


class MensajeriaService:
    def __init__(self, db: AsyncSession, tenant_id: uuid.UUID, current_user_id: uuid.UUID) -> None:
        self._mensaje_repo = MensajeRepository(db, tenant_id)
        self._usuario_repo = UsuarioRepository(db, tenant_id)
        self._tenant_id = tenant_id
        self._current_user_id = current_user_id

    async def list_inbox(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[Sequence[Mensaje], int]:
        return await self._mensaje_repo.list_by_destinatario(
            self._current_user_id,
            limit=limit,
            offset=offset,
        )

    async def get_mensaje(self, mensaje_id: uuid.UUID) -> MensajeOut:
        mensaje = await self._mensaje_repo.get_by_id_and_destinatario(
            mensaje_id,
            self._current_user_id,
        )
        mensaje = await self._mensaje_repo.marcar_leido(
            mensaje_id,
            self._current_user_id,
        )
        return MensajeOut.model_validate(mensaje)

    async def enviar_mensaje(self, data: MensajeCreate) -> MensajeOut:
        if data.destinatario_id == self._current_user_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No puedes enviarte un mensaje a ti mismo",
            )

        try:
            await self._usuario_repo.get(data.destinatario_id)
        except NotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario destinatario no encontrado",
            )

        hilo_id = uuid.uuid4()
        mensaje = await self._mensaje_repo.create(
            remitente_id=self._current_user_id,
            destinatario_id=data.destinatario_id,
            hilo_id=hilo_id,
            asunto=data.asunto,
            cuerpo=data.cuerpo,
        )
        return MensajeOut.model_validate(mensaje)

    async def responder_mensaje(
        self,
        mensaje_id: uuid.UUID,
        data: MensajeResponder,
    ) -> MensajeOut:
        try:
            mensaje_original = await self._mensaje_repo.get_by_id_and_destinatario(
                mensaje_id,
                self._current_user_id,
            )
        except NotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mensaje no encontrado",
            )

        hilo_id = mensaje_original.hilo_id or mensaje_original.id
        nuevo = await self._mensaje_repo.create(
            remitente_id=self._current_user_id,
            destinatario_id=mensaje_original.remitente_id,
            hilo_id=hilo_id,
            asunto=mensaje_original.asunto,
            cuerpo=data.cuerpo,
        )
        return MensajeOut.model_validate(nuevo)
