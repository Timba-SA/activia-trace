from __future__ import annotations

import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asignacion import Asignacion
from app.models.aviso import Aviso
from app.models.usuario_role import UsuarioRole
from app.repositories.aviso_repository import (
    AcknowledgmentRepository,
    AvisoRepository,
)
from app.schemas.aviso import (
    AvisoCreate,
    AvisoResponse,
    AvisoUpdate,
    AvisoStatsResponse,
)


class AvisosService:
    def __init__(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        current_user_id: uuid.UUID,
    ) -> None:
        self._db = db
        self._tenant_id = tenant_id
        self._current_user_id = current_user_id
        self._aviso_repo = AvisoRepository(db, tenant_id)
        self._ack_repo = AcknowledgmentRepository(db, tenant_id)

    async def crear_aviso(self, data: AvisoCreate) -> AvisoResponse:
        aviso = await self._aviso_repo.create(
            tenant_id=self._tenant_id,
            alcance=data.alcance,
            materia_id=data.materia_id,
            cohorte_id=data.cohorte_id,
            rol_destino=data.rol_destino,
            severidad=data.severidad,
            titulo=data.titulo,
            cuerpo=data.cuerpo,
            inicio_en=data.inicio_en,
            fin_en=data.fin_en,
            orden=data.orden,
            activo=data.activo,
            requiere_ack=data.requiere_ack,
        )
        return AvisoResponse(
            id=aviso.id,
            tenant_id=aviso.tenant_id,
            alcance=aviso.alcance,
            materia_id=aviso.materia_id,
            cohorte_id=aviso.cohorte_id,
            rol_destino=aviso.rol_destino,
            severidad=aviso.severidad,
            titulo=aviso.titulo,
            cuerpo=aviso.cuerpo,
            inicio_en=aviso.inicio_en,
            fin_en=aviso.fin_en,
            orden=aviso.orden,
            activo=aviso.activo,
            requiere_ack=aviso.requiere_ack,
            created_at=aviso.created_at,
            updated_at=aviso.updated_at,
        )

    async def actualizar_aviso(
        self, aviso_id: uuid.UUID, data: AvisoUpdate
    ) -> AvisoResponse:
        try:
            aviso = await self._aviso_repo.get(aviso_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aviso no encontrado",
            )

        update_kwargs = {}
        for field in [
            "alcance",
            "materia_id",
            "cohorte_id",
            "rol_destino",
            "severidad",
            "titulo",
            "cuerpo",
            "inicio_en",
            "fin_en",
            "orden",
            "activo",
            "requiere_ack",
        ]:
            value = getattr(data, field, None)
            if value is not None:
                update_kwargs[field] = value

        if update_kwargs:
            await self._aviso_repo.update(aviso_id, **update_kwargs)

        aviso = await self._aviso_repo.get(aviso_id)
        return AvisoResponse(
            id=aviso.id,
            tenant_id=aviso.tenant_id,
            alcance=aviso.alcance,
            materia_id=aviso.materia_id,
            cohorte_id=aviso.cohorte_id,
            rol_destino=aviso.rol_destino,
            severidad=aviso.severidad,
            titulo=aviso.titulo,
            cuerpo=aviso.cuerpo,
            inicio_en=aviso.inicio_en,
            fin_en=aviso.fin_en,
            orden=aviso.orden,
            activo=aviso.activo,
            requiere_ack=aviso.requiere_ack,
            created_at=aviso.created_at,
            updated_at=aviso.updated_at,
        )

    async def eliminar_aviso(self, aviso_id: uuid.UUID) -> None:
        try:
            await self._aviso_repo.soft_delete(aviso_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aviso no encontrado",
            )

    async def obtener_aviso(self, aviso_id: uuid.UUID) -> AvisoResponse:
        try:
            aviso = await self._aviso_repo.get(aviso_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aviso no encontrado",
            )
        return AvisoResponse(
            id=aviso.id,
            tenant_id=aviso.tenant_id,
            alcance=aviso.alcance,
            materia_id=aviso.materia_id,
            cohorte_id=aviso.cohorte_id,
            rol_destino=aviso.rol_destino,
            severidad=aviso.severidad,
            titulo=aviso.titulo,
            cuerpo=aviso.cuerpo,
            inicio_en=aviso.inicio_en,
            fin_en=aviso.fin_en,
            orden=aviso.orden,
            activo=aviso.activo,
            requiere_ack=aviso.requiere_ack,
            created_at=aviso.created_at,
            updated_at=aviso.updated_at,
        )

    async def listar_avisos(
        self,
        filters: dict[str, Any] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[AvisoResponse], int]:
        items, total = await self._aviso_repo.listar(
            filters=filters, limit=limit, offset=offset
        )
        results = [self._to_response(a) for a in items]
        return results, total

    async def listar_mis_avisos(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[AvisoResponse], int]:
        roles = await self._get_user_roles()
        materia_ids = await self._get_user_materias()
        cohorte_ids = await self._get_user_cohortes()

        usuario_context = {
            "roles": roles,
            "materia_ids": materia_ids,
            "cohorte_ids": cohorte_ids,
        }

        items, total = await self._aviso_repo.listar_visibles(
            usuario_context=usuario_context,
            limit=limit,
            offset=offset,
        )
        results = [self._to_response(a) for a in items]
        return results, total

    async def confirmar_lectura(
        self, aviso_id: uuid.UUID, usuario_id: uuid.UUID
    ) -> dict:
        try:
            aviso = await self._aviso_repo.get(aviso_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aviso no encontrado",
            )

        if not aviso.requiere_ack:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este aviso no requiere confirmación de lectura",
            )

        await self._ack_repo.create_or_ignore(aviso_id, usuario_id)
        return {"message": "Lectura confirmada"}

    async def obtener_stats(
        self, aviso_id: uuid.UUID
    ) -> AvisoStatsResponse:
        try:
            await self._aviso_repo.get(aviso_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aviso no encontrado",
            )

        total = await self._ack_repo.count_by_aviso(aviso_id)
        return AvisoStatsResponse(total_confirmaciones=total)

    async def _get_user_roles(self) -> list[str]:
        from app.models.role import Role
        user_roles_stmt = (
            select(Role.name)
            .join(UsuarioRole, UsuarioRole.role_id == Role.id)
            .where(
                UsuarioRole.usuario_id == self._current_user_id,
                UsuarioRole.tenant_id == self._tenant_id,
                Role.deleted_at.is_(None),
            )
        )
        role_result = await self._db.execute(user_roles_stmt)
        return [row[0] for row in role_result.all()]

    async def _get_user_materias(self) -> list[uuid.UUID]:
        stmt = (
            select(Asignacion.materia_id)
            .where(
                Asignacion.usuario_id == self._current_user_id,
                Asignacion.tenant_id == self._tenant_id,
                Asignacion.deleted_at.is_(None),
                Asignacion.materia_id.isnot(None),
                Asignacion.is_active == True,
            )
            .distinct()
        )
        result = await self._db.execute(stmt)
        return [row[0] for row in result.all()]

    async def _get_user_cohortes(self) -> list[uuid.UUID]:
        stmt = (
            select(Asignacion.cohorte_id)
            .where(
                Asignacion.usuario_id == self._current_user_id,
                Asignacion.tenant_id == self._tenant_id,
                Asignacion.deleted_at.is_(None),
                Asignacion.cohorte_id.isnot(None),
                Asignacion.is_active == True,
            )
            .distinct()
        )
        result = await self._db.execute(stmt)
        return [row[0] for row in result.all()]

    def _to_response(self, aviso: Aviso) -> AvisoResponse:
        return AvisoResponse(
            id=aviso.id,
            tenant_id=aviso.tenant_id,
            alcance=aviso.alcance,
            materia_id=aviso.materia_id,
            cohorte_id=aviso.cohorte_id,
            rol_destino=aviso.rol_destino,
            severidad=aviso.severidad,
            titulo=aviso.titulo,
            cuerpo=aviso.cuerpo,
            inicio_en=aviso.inicio_en,
            fin_en=aviso.fin_en,
            orden=aviso.orden,
            activo=aviso.activo,
            requiere_ack=aviso.requiere_ack,
            created_at=aviso.created_at,
            updated_at=aviso.updated_at,
        )
