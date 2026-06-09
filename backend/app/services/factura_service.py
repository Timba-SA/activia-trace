from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.factura import Factura
from app.repositories.factura_repository import FacturaRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.factura import FacturaCreate, FacturaEstadoUpdate, FacturaResponse


class FacturaService:
    def __init__(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
    ) -> None:
        self._factura_repo = FacturaRepository(db, tenant_id)
        self._usuario_repo = UsuarioRepository(db, tenant_id)
        self._tenant_id = tenant_id

    def _to_response(self, factura: Factura) -> FacturaResponse:
        return FacturaResponse(
            id=factura.id,
            tenant_id=factura.tenant_id,
            usuario_id=factura.usuario_id,
            periodo=factura.periodo,
            detalle=factura.detalle,
            referencia_archivo=factura.referencia_archivo,
            tamano_kb=float(factura.tamano_kb) if factura.tamano_kb else None,
            estado=factura.estado,
            cargada_at=factura.cargada_at,
            abonada_at=factura.abonada_at,
            created_at=factura.created_at,
            updated_at=factura.updated_at,
        )

    async def crear(self, data: FacturaCreate) -> FacturaResponse:
        try:
            usuario = await self._usuario_repo.get(data.usuario_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Docente no encontrado",
            )

        facturador = getattr(usuario, "facturador", False)
        if not facturador:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El docente no esta configurado como facturante",
            )

        factura = await self._factura_repo.create(
            tenant_id=self._tenant_id,
            usuario_id=data.usuario_id,
            periodo=data.periodo,
            detalle=data.detalle,
            referencia_archivo=data.referencia_archivo,
            tamano_kb=data.tamano_kb,
            estado="Pendiente",
        )
        return self._to_response(factura)

    async def listar(
        self,
        periodo: str | None = None,
        usuario_id: uuid.UUID | None = None,
        estado: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[FacturaResponse], int]:
        items, total = await self._factura_repo.list_by_filters(
            periodo=periodo,
            usuario_id=usuario_id,
            estado=estado,
            limit=limit,
            offset=offset,
        )
        return [self._to_response(f) for f in items], total

    async def cambiar_estado(
        self, factura_id: uuid.UUID, data: FacturaEstadoUpdate,
    ) -> FacturaResponse:
        try:
            factura = await self._factura_repo.get(factura_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Factura no encontrada",
            )

        nuevo_estado = data.estado
        if nuevo_estado not in ("Pendiente", "Abonada"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Estado invalido: {nuevo_estado}. Use Pendiente o Abonada",
            )

        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        update_kwargs = {"estado": nuevo_estado}
        if nuevo_estado == "Abonada":
            update_kwargs["abonada_at"] = now
        elif nuevo_estado == "Pendiente":
            update_kwargs["abonada_at"] = None

        await self._factura_repo.update(factura_id, **update_kwargs)
        factura = await self._factura_repo.get(factura_id)
        return self._to_response(factura)
