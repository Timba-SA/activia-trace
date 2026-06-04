from __future__ import annotations

import csv
import io
import uuid
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asignacion import Asignacion
from app.models.guardia import EstadoGuardia, Guardia
from app.repositories.guardia_repository import GuardiaRepository
from app.schemas.guardia import GuardiaCreate


class GuardiaService:
    def __init__(self, db: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._db = db
        self._tenant_id = tenant_id
        self._repo = GuardiaRepository(db, tenant_id)

    async def create(self, data: GuardiaCreate) -> Guardia:
        return await self._repo.create(
            tenant_id=self._tenant_id,
            asignacion_id=data.asignacion_id,
            materia_id=data.materia_id,
            carrera_id=data.carrera_id,
            cohorte_id=data.cohorte_id,
            dia=data.dia,
            horario=data.horario,
            estado=data.estado,
            comentarios=data.comentarios,
        )

    async def update_estado(
        self, guardia_id: uuid.UUID, estado: EstadoGuardia
    ) -> Guardia:
        try:
            guardia = await self._repo.get(guardia_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Guardia no encontrada",
            )

        if guardia.estado in (EstadoGuardia.REALIZADA, EstadoGuardia.CANCELADA):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede modificar una guardia realizada o cancelada",
            )

        return await self._repo.update(guardia_id, estado=estado)

    async def list_mis_guardias(
        self,
        usuario_id: uuid.UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Guardia], int, int]:
        stmt = select(Asignacion.id).where(
            Asignacion.usuario_id == usuario_id,
            Asignacion.tenant_id == self._tenant_id,
            Asignacion.deleted_at.is_(None),
        )
        result = await self._db.execute(stmt)
        asignacion_ids = [row[0] for row in result.fetchall()]

        if not asignacion_ids:
            return [], 0, 1

        return await self._repo.list_by_usuario(
            asignacion_ids=asignacion_ids,
            limit=limit,
            offset=offset,
        )

    async def list_guardias_admin(
        self,
        materia_id: uuid.UUID | None = None,
        carrera_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        asignacion_id: uuid.UUID | None = None,
        estado: EstadoGuardia | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Guardia], int, int]:
        return await self._repo.list_admin(
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            asignacion_id=asignacion_id,
            estado=estado,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            limit=limit,
            offset=offset,
        )

    async def exportar_csv(
        self,
        materia_id: uuid.UUID | None = None,
        carrera_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        asignacion_id: uuid.UUID | None = None,
        estado: EstadoGuardia | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> str:
        guardias = await self._repo.list_for_export(
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            asignacion_id=asignacion_id,
            estado=estado,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "id", "asignacion_id", "materia_id", "carrera_id", "cohorte_id",
            "dia", "horario", "estado", "comentarios", "creada_at",
        ])
        for g in guardias:
            writer.writerow([
                str(g.id),
                str(g.asignacion_id),
                str(g.materia_id),
                str(g.carrera_id),
                str(g.cohorte_id),
                g.dia.value if hasattr(g.dia, "value") else str(g.dia),
                g.horario,
                g.estado.value if hasattr(g.estado, "value") else str(g.estado),
                g.comentarios or "",
                g.creada_at.isoformat() if g.creada_at else "",
            ])
        csv_content = output.getvalue()
        output.close()
        return csv_content
