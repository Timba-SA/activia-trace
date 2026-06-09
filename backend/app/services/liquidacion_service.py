from __future__ import annotations

import csv
import io
import uuid
from datetime import date, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asignacion import Asignacion
from app.models.liquidacion import Liquidacion
from app.repositories.asignacion_repository import AsignacionRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.liquidacion_repository import LiquidacionRepository
from app.repositories.materia_grupo_plus_repository import MateriaGrupoPlusRepository
from app.repositories.salario_base_repository import SalarioBaseRepository
from app.repositories.salario_plus_repository import SalarioPlusRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.liquidacion import (
    ExportarRequest,
    LiquidacionCalcularRequest,
    LiquidacionCerrarResponse,
    LiquidacionListResponse,
    LiquidacionResponse,
)

_ROLES_NEXO = {"NEXO"}


def _periodo_to_date(periodo: str) -> date:
    parts = periodo.split("-")
    if len(parts) != 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Formato de periodo invalido: {periodo}. Use AAAA-MM",
        )
    try:
        return date(int(parts[0]), int(parts[1]), 1)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Formato de periodo invalido: {periodo}",
        )


class LiquidacionService:
    def __init__(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        current_user_id: uuid.UUID | None = None,
    ) -> None:
        self._db = db
        self._tenant_id = tenant_id
        self._current_user_id = current_user_id
        self._liquidacion_repo = LiquidacionRepository(db, tenant_id)
        self._salario_base_repo = SalarioBaseRepository(db, tenant_id)
        self._salario_plus_repo = SalarioPlusRepository(db, tenant_id)
        self._materia_grupo_repo = MateriaGrupoPlusRepository(db, tenant_id)
        self._asignacion_repo = AsignacionRepository(db, tenant_id)
        self._usuario_repo = UsuarioRepository(db, tenant_id)
        self._audit_repo = AuditLogRepository(db, tenant_id)

    def _to_response(self, liquidacion: Liquidacion) -> LiquidacionResponse:
        return LiquidacionResponse(
            id=liquidacion.id,
            tenant_id=liquidacion.tenant_id,
            cohorte_id=liquidacion.cohorte_id,
            periodo=liquidacion.periodo,
            usuario_id=liquidacion.usuario_id,
            rol=liquidacion.rol,
            comisiones=liquidacion.comisiones or [],
            monto_base=float(liquidacion.monto_base or 0),
            monto_plus=float(liquidacion.monto_plus or 0),
            total=float(liquidacion.total or 0),
            es_nexo=liquidacion.es_nexo or False,
            excluido_por_factura=liquidacion.excluido_por_factura or False,
            estado=liquidacion.estado,
            created_at=liquidacion.created_at,
            updated_at=liquidacion.updated_at,
        )

    async def calcular(
        self,
        request: LiquidacionCalcularRequest,
    ) -> list[LiquidacionResponse]:
        periodo_date = _periodo_to_date(request.periodo)

        existe = await self._liquidacion_repo.exists_for_periodo(
            request.cohorte_id, request.periodo,
        )
        if existe:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existen liquidaciones para la cohorte {request.cohorte_id} en periodo {request.periodo}",
            )

        asignaciones = await self._asignacion_repo.list_with_filters(
            {"cohorte_id": request.cohorte_id},
            limit=10000,
            offset=0,
        )
        all_asignaciones = asignaciones[0]
        if not all_asignaciones:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No se encontraron asignaciones activas para esta cohorte en el periodo",
            )

        docentes_map: dict[uuid.UUID, list[Asignacion]] = {}
        for asignacion in all_asignaciones:
            if asignacion.usuario_id not in docentes_map:
                docentes_map[asignacion.usuario_id] = []
            docentes_map[asignacion.usuario_id].append(asignacion)

        liquidaciones_data = []
        for usuario_id, asigns in docentes_map.items():
            if not asigns:
                continue

            rol = asigns[0].rol

            salario_base = await self._salario_base_repo.find_vigente(
                rol, periodo_date,
            )
            if salario_base is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"No se encontro SalarioBase vigente para rol {rol} en periodo {request.periodo} (usuario {usuario_id})",
                )

            materias_docente = [a for a in asigns if a.materia_id is not None]
            grupo_comisiones: dict[str, list[str]] = {}
            for asignacion in materias_docente:
                if asignacion.materia_id is None:
                    continue
                mgp = await self._materia_grupo_repo.find_vigente(
                    asignacion.materia_id, periodo_date,
                )
                if mgp is None:
                    continue
                if mgp.grupo not in grupo_comisiones:
                    grupo_comisiones[mgp.grupo] = []
                grupo_comisiones[mgp.grupo].append(asignacion.materia_id)

            monto_plus_total = 0.0
            comisiones_detalle: list[str] = []
            for grupo, materias_ids in grupo_comisiones.items():
                rol_a_usar = rol
                if rol_a_usar == "NEXO":
                    rol_a_usar = "NEXO"
                plus = await self._salario_plus_repo.find_vigente(
                    grupo, rol, periodo_date,
                )
                if plus is None:
                    continue

                n_comisiones = len(materias_ids)
                tope = plus.tope_acumulacion
                n_efectivas = (
                    min(n_comisiones, tope) if tope is not None else n_comisiones
                )
                monto_plus_parcial = float(plus.monto or 0) * n_efectivas
                monto_plus_total += monto_plus_parcial
                comisiones_detalle.append(
                    f"{grupo}:{n_comisiones}comisiones:{n_efectivas}efectivas"
                )

            monto_base = float(salario_base.monto or 0)
            total = monto_base + monto_plus_total

            es_nexo = rol in _ROLES_NEXO

            usuario = await self._usuario_repo.get(usuario_id)
            excluido = getattr(usuario, "facturador", False)

            liquidaciones_data.append({
                "tenant_id": self._tenant_id,
                "cohorte_id": request.cohorte_id,
                "periodo": request.periodo,
                "usuario_id": usuario_id,
                "rol": rol,
                "comisiones": comisiones_detalle,
                "monto_base": monto_base,
                "monto_plus": monto_plus_total,
                "total": total,
                "es_nexo": es_nexo,
                "excluido_por_factura": excluido,
                "estado": "Abierta",
            })

        created = await self._liquidacion_repo.bulk_create(liquidaciones_data)
        return [self._to_response(l) for l in created]

    async def listar(
        self,
        cohorte_id: uuid.UUID | None = None,
        periodo: str | None = None,
        usuario_id: uuid.UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[LiquidacionResponse], int]:
        items, total = await self._liquidacion_repo.find_by_filters(
            cohorte_id=cohorte_id,
            periodo=periodo,
            usuario_id=usuario_id,
            limit=limit,
            offset=offset,
        )
        return [self._to_response(l) for l in items], total

    async def obtener(self, liquidacion_id: uuid.UUID) -> LiquidacionResponse:
        try:
            liquidacion = await self._liquidacion_repo.get(liquidacion_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Liquidacion no encontrada",
            )
        return self._to_response(liquidacion)

    async def cerrar(
        self,
        liquidacion_id: uuid.UUID,
        actor_id: uuid.UUID,
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> LiquidacionCerrarResponse:
        try:
            liquidacion = await self._liquidacion_repo.get(liquidacion_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Liquidacion no encontrada",
            )

        if liquidacion.estado == "Cerrada":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La liquidacion ya esta cerrada",
            )

        await self._liquidacion_repo.update(liquidacion_id, estado="Cerrada")

        await self._audit_repo.create(
            tenant_id=self._tenant_id,
            actor_id=actor_id,
            accion="LIQUIDACION_CERRAR",
            detalle={
                "liquidacion_id": str(liquidacion_id),
                "periodo": liquidacion.periodo,
                "total": float(liquidacion.total),
                "cohorte_id": str(liquidacion.cohorte_id),
            },
            filas_afectadas=1,
            ip=ip or "",
            user_agent=user_agent or "",
        )

        liquidacion = await self._liquidacion_repo.get(liquidacion_id)
        return self._to_response(liquidacion)

    async def historial(
        self,
        cohorte_id: uuid.UUID | None = None,
        periodo: str | None = None,
        usuario_id: uuid.UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[LiquidacionResponse], int]:
        items, total = await self._liquidacion_repo.find_historial(
            cohorte_id=cohorte_id,
            periodo=periodo,
            usuario_id=usuario_id,
            limit=limit,
            offset=offset,
        )
        return [self._to_response(l) for l in items], total

    async def exportar(
        self,
        request: ExportarRequest,
    ) -> str:
        items, _ = await self._liquidacion_repo.find_by_filters(
            cohorte_id=request.cohorte_id,
            periodo=request.periodo,
            limit=10000,
            offset=0,
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "ID", "UsuarioID", "Rol", "Periodo",
            "MontoBase", "MontoPlus", "Total",
            "EsNexo", "ExcluidoPorFactura", "Estado", "Comisiones",
        ])
        for liq in items:
            writer.writerow([
                str(liq.id), str(liq.usuario_id), liq.rol, liq.periodo,
                float(liq.monto_base), float(liq.monto_plus), float(liq.total),
                liq.es_nexo, liq.excluido_por_factura, liq.estado,
                ",".join(liq.comisiones or []),
            ])

        return output.getvalue()
