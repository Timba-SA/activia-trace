import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.fecha_academica_repository import FechaAcademicaRepository
from app.schemas.fecha_academica import (
    FechaAcademicaCreate,
    FechaAcademicaResponse,
    FechaAcademicaUpdate,
)


class FechaAcademicaService:
    def __init__(self, db: AsyncSession, tenant_id: uuid.UUID, current_user_id: uuid.UUID):
        self._db = db
        self._tenant_id = tenant_id
        self._current_user_id = current_user_id
        self._repo = FechaAcademicaRepository(db, tenant_id)

    def _to_response(self, fa) -> FechaAcademicaResponse:
        return FechaAcademicaResponse(
            id=fa.id,
            tenant_id=fa.tenant_id,
            materia_id=fa.materia_id,
            cohorte_id=fa.cohorte_id,
            tipo=fa.tipo,
            numero=fa.numero,
            fecha=fa.fecha,
            hora=fa.hora,
            aula=fa.aula,
            observaciones=fa.observaciones,
            created_at=fa.created_at,
            updated_at=fa.updated_at,
        )

    async def create(self, data: FechaAcademicaCreate) -> FechaAcademicaResponse:
        fa = await self._repo.create(
            tenant_id=self._tenant_id,
            materia_id=data.materia_id,
            cohorte_id=data.cohorte_id,
            tipo=data.tipo,
            numero=data.numero,
            fecha=data.fecha,
            hora=data.hora,
            aula=data.aula,
            observaciones=data.observaciones,
        )
        return self._to_response(fa)

    async def update(self, id: uuid.UUID, data: FechaAcademicaUpdate) -> FechaAcademicaResponse:
        kwargs = {}
        if data.tipo is not None:
            kwargs["tipo"] = data.tipo
        if data.numero is not None:
            kwargs["numero"] = data.numero
        if data.fecha is not None:
            kwargs["fecha"] = data.fecha
        if data.hora is not None:
            kwargs["hora"] = data.hora
        if data.aula is not None:
            kwargs["aula"] = data.aula
        if data.observaciones is not None:
            kwargs["observaciones"] = data.observaciones
        try:
            fa = await self._repo.update(id, **kwargs)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fecha academica no encontrada",
            )
        return self._to_response(fa)

    async def delete(self, id: uuid.UUID) -> None:
        try:
            await self._repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fecha academica no encontrada",
            )
        await self._repo.soft_delete(id)

    async def list(
        self,
        filters: dict,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[FechaAcademicaResponse], int, int]:
        items, total, pages = await self._repo.list_filters(
            materia_id=filters.get("materia_id"),
            cohorte_id=filters.get("cohorte_id"),
            tipo=filters.get("tipo"),
            fecha_desde=filters.get("fecha_desde"),
            fecha_hasta=filters.get("fecha_hasta"),
            limit=limit,
            offset=offset,
        )
        results = [self._to_response(fa) for fa in items]
        return results, total, pages

    async def get_by_id(self, id: uuid.UUID) -> FechaAcademicaResponse:
        try:
            fa = await self._repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fecha academica no encontrada",
            )
        return self._to_response(fa)
