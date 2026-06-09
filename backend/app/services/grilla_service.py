from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.materia_grupo_plus_repository import MateriaGrupoPlusRepository
from app.repositories.salario_base_repository import SalarioBaseRepository
from app.repositories.salario_plus_repository import SalarioPlusRepository
from app.schemas.materia_grupo_plus import (
    MateriaGrupoPlusCreate,
    MateriaGrupoPlusResponse,
    MateriaGrupoPlusUpdate,
)
from app.schemas.salario_base import (
    SalarioBaseCreate,
    SalarioBaseResponse,
    SalarioBaseUpdate,
)
from app.schemas.salario_plus import (
    SalarioPlusCreate,
    SalarioPlusResponse,
    SalarioPlusUpdate,
)


class GrillaService:
    def __init__(self, db: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._tenant_id = tenant_id
        self._salario_base_repo = SalarioBaseRepository(db, tenant_id)
        self._salario_plus_repo = SalarioPlusRepository(db, tenant_id)
        self._materia_grupo_repo = MateriaGrupoPlusRepository(db, tenant_id)

    # SalarioBase
    async def crear_salario_base(
        self, data: SalarioBaseCreate,
    ) -> SalarioBaseResponse:
        overlap = await self._salario_base_repo.exists_overlap(
            data.rol, data.desde, data.hasta,
        )
        if overlap:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un SalarioBase vigente para el rol {data.rol} en el periodo {data.desde} - {data.hasta}",
            )
        instance = await self._salario_base_repo.create(
            tenant_id=self._tenant_id,
            rol=data.rol,
            monto=data.monto,
            desde=data.desde,
            hasta=data.hasta,
        )
        return SalarioBaseResponse(
            id=instance.id,
            tenant_id=instance.tenant_id,
            rol=instance.rol,
            monto=float(instance.monto),
            desde=instance.desde,
            hasta=instance.hasta,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

    async def listar_salarios_base(self) -> list[SalarioBaseResponse]:
        items = await self._salario_base_repo.list_all()
        return [
            SalarioBaseResponse(
                id=item.id,
                tenant_id=item.tenant_id,
                rol=item.rol,
                monto=float(item.monto),
                desde=item.desde,
                hasta=item.hasta,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in items
        ]

    async def actualizar_salario_base(
        self, id: uuid.UUID, data: SalarioBaseUpdate,
    ) -> SalarioBaseResponse:
        try:
            await self._salario_base_repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SalarioBase no encontrado",
            )
        update_kwargs = {}
        if data.monto is not None:
            update_kwargs["monto"] = data.monto
        if data.desde is not None:
            update_kwargs["desde"] = data.desde
        if data.hasta is not None:
            update_kwargs["hasta"] = data.hasta
        if update_kwargs:
            await self._salario_base_repo.update(id, **update_kwargs)
        item = await self._salario_base_repo.get(id)
        return SalarioBaseResponse(
            id=item.id,
            tenant_id=item.tenant_id,
            rol=item.rol,
            monto=float(item.monto),
            desde=item.desde,
            hasta=item.hasta,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    async def eliminar_salario_base(self, id: uuid.UUID) -> None:
        try:
            await self._salario_base_repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SalarioBase no encontrado",
            )
        await self._salario_base_repo.soft_delete(id)

    # SalarioPlus
    async def crear_salario_plus(
        self, data: SalarioPlusCreate,
    ) -> SalarioPlusResponse:
        instance = await self._salario_plus_repo.create(
            tenant_id=self._tenant_id,
            grupo=data.grupo,
            rol=data.rol,
            descripcion=data.descripcion,
            monto=data.monto,
            tope_acumulacion=data.tope_acumulacion,
            desde=data.desde,
            hasta=data.hasta,
        )
        return SalarioPlusResponse(
            id=instance.id,
            tenant_id=instance.tenant_id,
            grupo=instance.grupo,
            rol=instance.rol,
            descripcion=instance.descripcion,
            monto=float(instance.monto),
            tope_acumulacion=instance.tope_acumulacion,
            desde=instance.desde,
            hasta=instance.hasta,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

    async def listar_salarios_plus(self) -> list[SalarioPlusResponse]:
        items = await self._salario_plus_repo.list_all()
        return [
            SalarioPlusResponse(
                id=item.id,
                tenant_id=item.tenant_id,
                grupo=item.grupo,
                rol=item.rol,
                descripcion=item.descripcion,
                monto=float(item.monto),
                tope_acumulacion=item.tope_acumulacion,
                desde=item.desde,
                hasta=item.hasta,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in items
        ]

    async def actualizar_salario_plus(
        self, id: uuid.UUID, data: SalarioPlusUpdate,
    ) -> SalarioPlusResponse:
        try:
            await self._salario_plus_repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SalarioPlus no encontrado",
            )
        update_kwargs = {}
        for field in ("grupo", "rol", "descripcion", "monto", "tope_acumulacion", "desde", "hasta"):
            val = getattr(data, field, None)
            if val is not None:
                update_kwargs[field] = val
        if update_kwargs:
            await self._salario_plus_repo.update(id, **update_kwargs)
        item = await self._salario_plus_repo.get(id)
        return SalarioPlusResponse(
            id=item.id,
            tenant_id=item.tenant_id,
            grupo=item.grupo,
            rol=item.rol,
            descripcion=item.descripcion,
            monto=float(item.monto),
            tope_acumulacion=item.tope_acumulacion,
            desde=item.desde,
            hasta=item.hasta,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    async def eliminar_salario_plus(self, id: uuid.UUID) -> None:
        try:
            await self._salario_plus_repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SalarioPlus no encontrado",
            )
        await self._salario_plus_repo.soft_delete(id)

    # MateriaGrupoPlus
    async def crear_materia_grupo(
        self, data: MateriaGrupoPlusCreate,
    ) -> MateriaGrupoPlusResponse:
        exists = await self._materia_grupo_repo.exists_vigente(
            data.materia_id, data.grupo, data.desde, data.hasta,
        )
        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un mapeo vigente para la materia {data.materia_id} con grupo {data.grupo} en el periodo {data.desde} - {data.hasta}",
            )
        instance = await self._materia_grupo_repo.create(
            tenant_id=self._tenant_id,
            materia_id=data.materia_id,
            grupo=data.grupo,
            desde=data.desde,
            hasta=data.hasta,
        )
        return MateriaGrupoPlusResponse(
            id=instance.id,
            tenant_id=instance.tenant_id,
            materia_id=instance.materia_id,
            grupo=instance.grupo,
            desde=instance.desde,
            hasta=instance.hasta,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )

    async def listar_materias_grupo(self) -> list[MateriaGrupoPlusResponse]:
        items = await self._materia_grupo_repo.list_all()
        return [
            MateriaGrupoPlusResponse(
                id=item.id,
                tenant_id=item.tenant_id,
                materia_id=item.materia_id,
                grupo=item.grupo,
                desde=item.desde,
                hasta=item.hasta,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in items
        ]

    async def actualizar_materia_grupo(
        self, id: uuid.UUID, data: MateriaGrupoPlusUpdate,
    ) -> MateriaGrupoPlusResponse:
        try:
            await self._materia_grupo_repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MateriaGrupoPlus no encontrado",
            )
        update_kwargs = {}
        if data.grupo is not None:
            update_kwargs["grupo"] = data.grupo
        if data.desde is not None:
            update_kwargs["desde"] = data.desde
        if data.hasta is not None:
            update_kwargs["hasta"] = data.hasta
        if update_kwargs:
            await self._materia_grupo_repo.update(id, **update_kwargs)
        item = await self._materia_grupo_repo.get(id)
        return MateriaGrupoPlusResponse(
            id=item.id,
            tenant_id=item.tenant_id,
            materia_id=item.materia_id,
            grupo=item.grupo,
            desde=item.desde,
            hasta=item.hasta,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    async def eliminar_materia_grupo(self, id: uuid.UUID) -> None:
        try:
            await self._materia_grupo_repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MateriaGrupoPlus no encontrado",
            )
        await self._materia_grupo_repo.soft_delete(id)
