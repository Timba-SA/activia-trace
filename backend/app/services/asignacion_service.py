from __future__ import annotations

import csv
import io
import uuid
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asignacion import Asignacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.models.usuario import Usuario
from app.repositories.asignacion_repository import AsignacionRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.asignacion import (
    AsignacionCreate,
    AsignacionUpdate,
    AsignacionMasivaRequest,
    CloneRequest,
    VigenciaUpdateRequest,
)


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

    # ── Equipos docentes ─────────────────────────────────────────────────

    async def mis_equipos(
        self,
        usuario_id: uuid.UUID,
        estado: str | None = None,
        materia_id: uuid.UUID | None = None,
        rol: str | None = None,
        carrera_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Asignacion], int, int]:
        filters: dict = {}
        if estado is not None:
            filters["estado"] = estado
        if materia_id is not None:
            filters["materia_id"] = materia_id
        if rol is not None:
            filters["rol"] = rol
        if carrera_id is not None:
            filters["carrera_id"] = carrera_id
        if cohorte_id is not None:
            filters["cohorte_id"] = cohorte_id
        items, total, pages = await self._repo.list_with_filters(
            filters,
            usuario_id=usuario_id,
            limit=limit,
            offset=offset,
        )
        return list(items), total, pages

    async def list_equipos(
        self,
        materia_id: uuid.UUID | None = None,
        carrera_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        usuario_id: uuid.UUID | None = None,
        nombre: str | None = None,
        rol: str | None = None,
        responsable_id: uuid.UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Asignacion], int, int]:
        filters: dict = {}
        if materia_id is not None:
            filters["materia_id"] = materia_id
        if carrera_id is not None:
            filters["carrera_id"] = carrera_id
        if cohorte_id is not None:
            filters["cohorte_id"] = cohorte_id
        if usuario_id is not None:
            filters["usuario_id"] = usuario_id
        if rol is not None:
            filters["rol"] = rol
        if responsable_id is not None:
            filters["responsable_id"] = responsable_id
        if nombre is not None:
            filters["nombre"] = nombre

        if nombre is not None:
            stmt = (
                select(Asignacion)
                .join(Usuario, Asignacion.usuario_id == Usuario.id)
                .where(
                    Asignacion.tenant_id == self._tenant_id,
                    Asignacion.deleted_at.is_(None),
                    Usuario.tenant_id == self._tenant_id,
                )
            )
            if materia_id is not None:
                stmt = stmt.where(Asignacion.materia_id == materia_id)
            if carrera_id is not None:
                stmt = stmt.where(Asignacion.carrera_id == carrera_id)
            if cohorte_id is not None:
                stmt = stmt.where(Asignacion.cohorte_id == cohorte_id)
            if usuario_id is not None:
                stmt = stmt.where(Asignacion.usuario_id == usuario_id)
            if rol is not None:
                stmt = stmt.where(Asignacion.rol == rol)
            if responsable_id is not None:
                stmt = stmt.where(Asignacion.responsable_id == responsable_id)
            if nombre is not None:
                pattern = f"%{nombre}%"
                stmt = stmt.where(
                    Usuario.nombre.ilike(pattern) | Usuario.apellido.ilike(pattern),
                )

            count_stmt = select(func.count()).select_from(stmt.subquery())
            count_result = await self._db.execute(count_stmt)
            total = count_result.scalar_one()
            stmt = stmt.limit(limit).offset(offset)
            result = await self._db.execute(stmt)
            items = list(result.scalars().all())
            pages = max(1, (total + limit - 1) // limit) if limit > 0 else 1
            return items, total, pages

        items, total, pages = await self._repo.list_with_filters(
            filters,
            limit=limit,
            offset=offset,
        )
        return list(items), total, pages

    async def asignacion_masiva(self, body: AsignacionMasivaRequest) -> list[Asignacion]:
        if not body.usuario_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="usuario_ids must not be empty",
            )

        stmt = select(Usuario.id).where(
            Usuario.id.in_(body.usuario_ids),
            Usuario.tenant_id == self._tenant_id,
        )
        result = await self._db.execute(stmt)
        existing_ids = {row[0] for row in result.fetchall()}
        missing = [str(uid) for uid in body.usuario_ids if uid not in existing_ids]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Usuarios not found: {', '.join(missing)}",
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

        entries = [
            {
                "tenant_id": self._tenant_id,
                "usuario_id": uid,
                "rol": body.rol,
                "carrera_id": body.carrera_id,
                "materia_id": body.materia_id,
                "cohorte_id": body.cohorte_id,
                "responsable_id": body.responsable_id,
                "fecha_inicio": body.fecha_inicio,
                "fecha_fin": body.fecha_fin,
                "comisiones": body.comisiones or [],
            }
            for uid in body.usuario_ids
        ]
        return await self._repo.bulk_create(entries)

    async def clonar(self, body: CloneRequest) -> list[Asignacion]:
        await self._validate_fk(Cohorte, body.cohorte_destino_id, "Cohorte destino")

        source = await self._repo.list_by_team_scope(
            materia_id=body.materia_id,
            carrera_id=body.carrera_id,
            cohorte_id=body.cohorte_origen_id,
        )
        if not source:
            return []

        entries = [
            {
                "tenant_id": self._tenant_id,
                "usuario_id": a.usuario_id,
                "rol": a.rol,
                "carrera_id": a.carrera_id,
                "materia_id": a.materia_id,
                "cohorte_id": body.cohorte_destino_id,
                "responsable_id": a.responsable_id,
                "fecha_inicio": body.fecha_inicio,
                "fecha_fin": body.fecha_fin,
                "comisiones": a.comisiones or [],
            }
            for a in source
        ]
        return await self._repo.bulk_create(entries)

    async def update_vigencia_equipo(self, body: VigenciaUpdateRequest) -> int:
        affected = await self._repo.update_vigencia_by_team(
            materia_id=body.materia_id,
            carrera_id=body.carrera_id,
            cohorte_id=body.cohorte_id,
            fecha_inicio=body.fecha_inicio,
            fecha_fin=body.fecha_fin,
        )
        return affected

    async def exportar_equipo(
        self,
        materia_id: uuid.UUID,
        carrera_id: uuid.UUID,
        cohorte_id: uuid.UUID,
    ) -> str:
        stmt = (
            select(Asignacion, Usuario.nombre, Usuario.apellido)
            .join(Usuario, Asignacion.usuario_id == Usuario.id)
            .where(
                Asignacion.tenant_id == self._tenant_id,
                Asignacion.deleted_at.is_(None),
                Asignacion.materia_id == materia_id,
                Asignacion.carrera_id == carrera_id,
                Asignacion.cohorte_id == cohorte_id,
            )
        )
        result = await self._db.execute(stmt)
        rows = result.all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["docente", "rol", "materia_id", "carrera_id", "cohorte_id", "comisiones", "fecha_inicio", "fecha_fin", "estado"])
        for asignacion, nombre, apellido in rows:
            docente = f"{nombre or ''} {apellido or ''}".strip()
            hoy = date.today()
            if asignacion.fecha_fin and asignacion.fecha_fin < hoy:
                estado = "vencida"
            else:
                estado = "vigente"
            writer.writerow([
                docente,
                asignacion.rol,
                str(asignacion.materia_id) if asignacion.materia_id else "",
                str(asignacion.carrera_id) if asignacion.carrera_id else "",
                str(asignacion.cohorte_id) if asignacion.cohorte_id else "",
                ",".join(asignacion.comisiones or []),
                asignacion.fecha_inicio.isoformat(),
                asignacion.fecha_fin.isoformat() if asignacion.fecha_fin else "",
                estado,
            ])
        csv_content = output.getvalue()
        output.close()
        return csv_content
