from __future__ import annotations

import uuid
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asignacion import Asignacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.models.usuario import Usuario
from app.repositories.asignacion_repository import AsignacionRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.asignacion import AsignacionCreate, AsignacionUpdate


class AsignacionService:
    def __init__(self, db: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._repo = AsignacionRepository(db, tenant_id)
        self._db = db
        self._tenant_id = tenant_id
        self._usuario_repo = UsuarioRepository(db, tenant_id)

    async def _validate_fk(self, model_class, id: uuid.UUID | None, label: str) -> None:
        if id is None:
            return
        stmt = select(model_class).where(
            model_class.id == id,
            model_class.tenant_id == self._tenant_id,
        )
        result = await self._db.execute(stmt)
        if result.scalars().first() is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{label} not found",
            )

    async def create(self, body: AsignacionCreate) -> Asignacion:
        stmt = select(Usuario).where(
            Usuario.id == body.usuario_id,
            Usuario.tenant_id == self._tenant_id,
        )
        result = await self._db.execute(stmt)
        if result.scalars().first() is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario not found",
            )

        await self._validate_fk(Carrera, body.carrera_id, "Carrera")
        await self._validate_fk(Materia, body.materia_id, "Materia")
        await self._validate_fk(Cohorte, body.cohorte_id, "Cohorte")
        if body.responsable_id:
            stmt = select(Usuario).where(
                Usuario.id == body.responsable_id,
                Usuario.tenant_id == self._tenant_id,
            )
            result = await self._db.execute(stmt)
            if result.scalars().first() is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Responsable not found",
                )

        return await self._repo.create(
            tenant_id=self._tenant_id,
            usuario_id=body.usuario_id,
            rol=body.rol,
            carrera_id=body.carrera_id,
            materia_id=body.materia_id,
            cohorte_id=body.cohorte_id,
            responsable_id=body.responsable_id,
            fecha_inicio=body.fecha_inicio or date.today(),
            fecha_fin=body.fecha_fin,
            comisiones=body.comisiones or [],
        )

    async def get(self, id: uuid.UUID) -> Asignacion:
        try:
            return await self._repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asignacion not found",
            )

    async def list(self, limit: int = 20, offset: int = 0) -> tuple[list[Asignacion], int, int]:
        items, total, pages = await self._repo.paginate(limit=limit, offset=offset)
        return list(items), total, pages

    async def update(self, id: uuid.UUID, body: AsignacionUpdate) -> Asignacion:
        try:
            await self._repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asignacion not found",
            )
        kwargs = {}
        if body.rol is not None:
            kwargs["rol"] = body.rol
        if body.fecha_inicio is not None:
            kwargs["fecha_inicio"] = body.fecha_inicio
        if body.fecha_fin is not None:
            kwargs["fecha_fin"] = body.fecha_fin
        if body.comisiones is not None:
            kwargs["comisiones"] = body.comisiones
        if body.is_active is not None:
            kwargs["is_active"] = body.is_active
        return await self._repo.update(id, **kwargs)

    async def soft_delete(self, id: uuid.UUID) -> None:
        try:
            await self._repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asignacion not found",
            )
        await self._repo.soft_delete(id)

    async def list_by_usuario(self, usuario_id: uuid.UUID) -> list[Asignacion]:
        stmt = select(Usuario).where(
            Usuario.id == usuario_id,
            Usuario.tenant_id == self._tenant_id,
        )
        result = await self._db.execute(stmt)
        if result.scalars().first() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario not found",
            )
        return await self._repo.list_by_usuario(usuario_id)
