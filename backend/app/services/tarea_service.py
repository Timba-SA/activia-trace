from __future__ import annotations

import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tarea import EstadoTarea, Tarea
from app.repositories.tarea_repository import (
    ComentarioTareaRepository,
    TareaRepository,
)
from app.schemas.tarea import (
    ComentarioTareaResponse,
    TareaCreate,
    TareaResponse,
    TareaUpdate,
)

_TRANSICIONES_BASE: dict[EstadoTarea, set[EstadoTarea]] = {
    EstadoTarea.PENDIENTE: {EstadoTarea.EN_PROGRESO},
    EstadoTarea.EN_PROGRESO: {EstadoTarea.RESUELTA},
    EstadoTarea.RESUELTA: set(),
    EstadoTarea.CANCELADA: set(),
}

_TRANSICIONES_COORDINADOR: dict[EstadoTarea, set[EstadoTarea]] = {
    EstadoTarea.PENDIENTE: {EstadoTarea.CANCELADA},
    EstadoTarea.EN_PROGRESO: {EstadoTarea.CANCELADA},
    EstadoTarea.RESUELTA: {EstadoTarea.PENDIENTE, EstadoTarea.CANCELADA},
    EstadoTarea.CANCELADA: set(),
}

_ROLES_COORDINADOR_ADMIN = {"COORDINADOR", "ADMIN"}


class TareasService:
    def __init__(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        current_user_id: uuid.UUID,
        current_user_roles: list[str],
    ) -> None:
        self._db = db
        self._tenant_id = tenant_id
        self._current_user_id = current_user_id
        self._current_user_roles = [r.upper() for r in current_user_roles]
        self._tarea_repo = TareaRepository(db, tenant_id)
        self._comentario_repo = ComentarioTareaRepository(db, tenant_id)

    def _is_coordinador_admin(self) -> bool:
        return bool(set(self._current_user_roles) & _ROLES_COORDINADOR_ADMIN)

    def _to_response(self, tarea: Tarea) -> TareaResponse:
        return TareaResponse(
            id=tarea.id,
            tenant_id=tarea.tenant_id,
            estado=tarea.estado,
            asignado_a=tarea.asignado_a,
            asignado_por=tarea.asignado_por,
            materia_id=tarea.materia_id,
            contexto_id=tarea.contexto_id,
            descripcion=tarea.descripcion,
            created_at=tarea.created_at,
            updated_at=tarea.updated_at,
        )

    async def crear_tarea(self, data: TareaCreate, asignado_por_id: uuid.UUID) -> TareaResponse:
        tarea = await self._tarea_repo.create(
            tenant_id=self._tenant_id,
            estado=EstadoTarea.PENDIENTE,
            asignado_a=data.asignado_a,
            asignado_por=asignado_por_id,
            materia_id=data.materia_id,
            contexto_id=data.contexto_id,
            descripcion=data.descripcion,
        )
        return self._to_response(tarea)

    async def obtener_tarea(self, tarea_id: uuid.UUID) -> TareaResponse:
        try:
            tarea = await self._tarea_repo.get(tarea_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada",
            )
        return self._to_response(tarea)

    async def actualizar_tarea(
        self, tarea_id: uuid.UUID, data: TareaUpdate
    ) -> TareaResponse:
        try:
            tarea = await self._tarea_repo.get(tarea_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada",
            )
        update_kwargs = {}
        if data.estado is not None:
            update_kwargs["estado"] = data.estado
        if data.asignado_a is not None:
            update_kwargs["asignado_a"] = data.asignado_a
        if data.descripcion is not None:
            update_kwargs["descripcion"] = data.descripcion
        if update_kwargs:
            await self._tarea_repo.update(tarea_id, **update_kwargs)
        tarea = await self._tarea_repo.get(tarea_id)
        return self._to_response(tarea)

    async def listar_mis_tareas(
        self, usuario_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> tuple[list[TareaResponse], int]:
        items, total = await self._tarea_repo.listar_mis_tareas(
            usuario_id=usuario_id, limit=limit, offset=offset
        )
        results = [self._to_response(t) for t in items]
        return results, total

    async def listar_tareas_admin(
        self,
        filtros: dict[str, Any] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[TareaResponse], int]:
        items, total = await self._tarea_repo.listar_admin(
            filtros=filtros, limit=limit, offset=offset
        )
        results = [self._to_response(t) for t in items]
        return results, total

    async def cambiar_estado(
        self,
        tarea_id: uuid.UUID,
        nuevo_estado: EstadoTarea,
    ) -> TareaResponse:
        try:
            tarea = await self._tarea_repo.get(tarea_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada",
            )

        estado_actual = tarea.estado
        es_coordinador_admin = self._is_coordinador_admin()

        transiciones_permitidas = set(_TRANSICIONES_BASE.get(estado_actual, set()))
        if es_coordinador_admin:
            transiciones_permitidas.update(
                _TRANSICIONES_COORDINADOR.get(estado_actual, set())
            )

        if nuevo_estado not in transiciones_permitidas:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Transicion invalida: {estado_actual.value} -> {nuevo_estado.value}",
            )

        await self._tarea_repo.update(tarea_id, estado=nuevo_estado)
        tarea = await self._tarea_repo.get(tarea_id)
        return self._to_response(tarea)

    async def agregar_comentario(
        self, tarea_id: uuid.UUID, autor_id: uuid.UUID, texto: str
    ) -> ComentarioTareaResponse:
        try:
            await self._tarea_repo.get(tarea_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada",
            )

        comentario = await self._comentario_repo.crear_comentario(
            tarea_id=tarea_id,
            autor_id=autor_id,
            texto=texto,
        )
        return ComentarioTareaResponse(
            id=comentario.id,
            tarea_id=comentario.tarea_id,
            autor_id=comentario.autor_id,
            texto=comentario.texto,
            creado_at=comentario.creado_at,
        )

    async def listar_comentarios(
        self, tarea_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> tuple[list[ComentarioTareaResponse], int]:
        items, total = await self._comentario_repo.listar_por_tarea(
            tarea_id=tarea_id, limit=limit, offset=offset
        )
        results = [
            ComentarioTareaResponse(
                id=c.id,
                tarea_id=c.tarea_id,
                autor_id=c.autor_id,
                texto=c.texto,
                creado_at=c.creado_at,
            )
            for c in items
        ]
        return results, total
