from __future__ import annotations

import uuid
from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.encuentro_instancia import EstadoInstancia, InstanciaEncuentro
from app.models.encuentro_slot import DiaSemana, SlotEncuentro
from app.repositories.encuentro_repository import (
    InstanciaEncuentroRepository,
    SlotEncuentroRepository,
)
from app.schemas.encuentro import (
    InstanciaEncuentroCreate,
    InstanciaEncuentroUpdate,
    SlotEncuentroCreate,
)


class EncuentroService:
    def __init__(self, db: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._db = db
        self._tenant_id = tenant_id
        self._slot_repo = SlotEncuentroRepository(db, tenant_id)
        self._instancia_repo = InstanciaEncuentroRepository(db, tenant_id)

    async def create_slot(self, data: SlotEncuentroCreate) -> SlotEncuentro:
        if data.cant_semanas == 0 and data.fecha_unica is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Debe especificar modo recurrente (cant_semanas > 0) o fecha única (fecha_unica)",
            )
        if data.cant_semanas > 0 and data.fecha_unica is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Los modos recurrente y fecha única son mutuamente excluyentes",
            )
        if data.cant_semanas > 52:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El máximo de semanas es 52",
            )

        slot = await self._slot_repo.create(
            tenant_id=self._tenant_id,
            asignacion_id=data.asignacion_id,
            materia_id=data.materia_id,
            titulo=data.titulo,
            hora=data.hora,
            dia_semana=data.dia_semana,
            fecha_inicio=data.fecha_inicio,
            cant_semanas=data.cant_semanas,
            fecha_unica=data.fecha_unica,
            meet_url=data.meet_url,
            vig_desde=data.vig_desde,
            vig_hasta=data.vig_hasta,
        )

        if data.cant_semanas > 0:
            for i in range(data.cant_semanas):
                instancia_fecha = data.fecha_inicio + timedelta(weeks=i)
                await self._instancia_repo.create(
                    tenant_id=self._tenant_id,
                    slot_id=slot.id,
                    materia_id=data.materia_id,
                    fecha=instancia_fecha,
                    hora=data.hora,
                    titulo=data.titulo,
                    estado=EstadoInstancia.PROGRAMADO,
                    meet_url=data.meet_url,
                )
        elif data.fecha_unica is not None:
            await self._instancia_repo.create(
                tenant_id=self._tenant_id,
                slot_id=slot.id,
                materia_id=data.materia_id,
                fecha=data.fecha_unica,
                hora=data.hora,
                titulo=data.titulo,
                estado=EstadoInstancia.PROGRAMADO,
                meet_url=data.meet_url,
            )

        return slot

    async def create_instancia_independiente(
        self, data: InstanciaEncuentroCreate
    ) -> InstanciaEncuentro:
        return await self._instancia_repo.create(
            tenant_id=self._tenant_id,
            slot_id=data.slot_id,
            materia_id=data.materia_id,
            fecha=data.fecha,
            hora=data.hora,
            titulo=data.titulo,
            estado=EstadoInstancia.PROGRAMADO,
            meet_url=data.meet_url,
        )

    async def update_instancia(
        self, instancia_id: uuid.UUID, data: InstanciaEncuentroUpdate
    ) -> InstanciaEncuentro:
        try:
            return await self._instancia_repo.update(
                instancia_id,
                estado=data.estado,
                meet_url=data.meet_url,
                video_url=data.video_url,
                comentario=data.comentario,
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instancia de encuentro no encontrada",
            )

    async def list_slots(
        self,
        materia_id: uuid.UUID | None = None,
        asignacion_id: uuid.UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[SlotEncuentro], int, int]:
        return await self._slot_repo.list_by_filters(
            materia_id=materia_id,
            asignacion_id=asignacion_id,
            limit=limit,
            offset=offset,
        )

    async def list_instancias_por_slot(
        self,
        slot_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[InstanciaEncuentro], int, int]:
        return await self._instancia_repo.list_by_slot(
            slot_id=slot_id,
            limit=limit,
            offset=offset,
        )

    async def list_instancias_admin(
        self,
        materia_id: uuid.UUID | None = None,
        estado: EstadoInstancia | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[InstanciaEncuentro], int, int]:
        return await self._instancia_repo.list_admin(
            materia_id=materia_id,
            estado=estado,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            limit=limit,
            offset=offset,
        )

    async def exportar_html(
        self,
        materia_id: uuid.UUID,
    ) -> str:
        instancias = await self._instancia_repo.list_futuras(
            materia_id=materia_id,
        )

        rows_html = ""
        for instancia in instancias:
            video_link = ""
            if instancia.estado == EstadoInstancia.REALIZADO and instancia.video_url:
                video_link = f'<a href="{instancia.video_url}" target="_blank">Ver grabación</a>'
            elif instancia.estado == EstadoInstancia.PROGRAMADO and instancia.meet_url:
                video_link = f'<a href="{instancia.meet_url}" target="_blank">Unirse</a>'

            rows_html += (
                f"<tr>"
                f"<td>{instancia.fecha.isoformat()}</td>"
                f"<td>{instancia.hora.isoformat()[:5]}</td>"
                f"<td>{instancia.titulo}</td>"
                f"<td>{instancia.estado.value}</td>"
                f"<td>{video_link}</td>"
                f"</tr>\n"
            )

        html = (
            f'<table class="encuentros-table">\n'
            f"<thead>\n"
            f"<tr><th>Fecha</th><th>Horario</th><th>Título</th><th>Estado</th><th>Enlace</th></tr>\n"
            f"</thead>\n"
            f"<tbody>\n"
            f"{rows_html}"
            f"</tbody>\n"
            f"</table>"
        )
        return html
