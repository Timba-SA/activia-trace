from __future__ import annotations

import uuid
from typing import Any

from fastapi import HTTPException, status

from app.models.aviso import Aviso
from app.repositories.asignacion_repository import AsignacionRepository
from app.repositories.aviso_repository import (
    AcknowledgmentRepository,
    AvisoRepository,
)
from app.repositories.role_repository import UsuarioRoleRepository
from app.schemas.aviso import (
    AvisoCreate,
    AvisoResponse,
    AvisoUpdate,
    AvisoStatsResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession


class AvisosService:
    def __init__(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        current_user_id: uuid.UUID,
    ) -> None:
        self._tenant_id = tenant_id
        self._current_user_id = current_user_id
        self._aviso_repo = AvisoRepository(db, tenant_id)
        self._ack_repo = AcknowledgmentRepository(db, tenant_id)
        self._usuario_role_repo = UsuarioRoleRepository(db, tenant_id)
        self._asignacion_repo = AsignacionRepository(db, tenant_id)

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
        return self._to_response(aviso)

    async def actualizar_aviso(
        self, aviso_id: uuid.UUID, data: AvisoUpdate
    ) -> AvisoResponse:
        try:
            await self._aviso_repo.get(aviso_id)
        except Exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aviso no encontrado")

        update_kwargs = {}
        for field in [
            "alcance", "materia_id", "cohorte_id", "rol_destino", "severidad",
            "titulo", "cuerpo", "inicio_en", "fin_en", "orden", "activo", "requiere_ack",
        ]:
            value = getattr(data, field, None)
            if value is not None:
                update_kwargs[field] = value

        if update_kwargs:
            await self._aviso_repo.update(aviso_id, **update_kwargs)

        aviso = await self._aviso_repo.get(aviso_id)
        return self._to_response(aviso)

    async def eliminar_aviso(self, aviso_id: uuid.UUID) -> None:
        try:
            await self._aviso_repo.soft_delete(aviso_id)
        except Exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aviso no encontrado")

    async def obtener_aviso(self, aviso_id: uuid.UUID) -> AvisoResponse:
        try:
            aviso = await self._aviso_repo.get(aviso_id)
        except Exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aviso no encontrado")
        return self._to_response(aviso)

    async def listar_avisos(
        self,
        filters: dict[str, Any] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[AvisoResponse], int]:
        items, total = await self._aviso_repo.listar(
            filters=filters, limit=limit, offset=offset
        )
        return [self._to_response(a) for a in items], total

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
        return [self._to_response(a) for a in items], total

    async def confirmar_lectura(
        self, aviso_id: uuid.UUID, usuario_id: uuid.UUID
    ) -> dict:
        try:
            aviso = await self._aviso_repo.get(aviso_id)
        except Exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aviso no encontrado")

        if not aviso.requiere_ack:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este aviso no requiere confirmación de lectura",
            )

        await self._ack_repo.create_or_ignore(aviso_id, usuario_id)
        return {"message": "Lectura confirmada"}

    async def obtener_stats(self, aviso_id: uuid.UUID) -> AvisoStatsResponse:
        try:
            await self._aviso_repo.get(aviso_id)
        except Exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aviso no encontrado")

        total = await self._ack_repo.count_by_aviso(aviso_id)
        return AvisoStatsResponse(total_confirmaciones=total)

    async def _get_user_roles(self) -> list[str]:
        return await self._usuario_role_repo.get_user_role_names(self._current_user_id)

    async def _get_user_materias(self) -> list[uuid.UUID]:
        return await self._asignacion_repo.list_materia_ids_by_usuario(self._current_user_id)

    async def _get_user_cohortes(self) -> list[uuid.UUID]:
        return await self._asignacion_repo.list_cohorte_ids_by_usuario(self._current_user_id)

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
