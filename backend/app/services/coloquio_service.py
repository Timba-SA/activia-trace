from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.convocatoria_alumno import ConvocatoriaAlumno
from app.models.evaluacion import Evaluacion, TipoEvaluacion
from app.models.reserva_evaluacion import EstadoReserva, ReservaEvaluacion
from app.models.resultado_evaluacion import ResultadoEvaluacion
from app.models.role import Role
from app.models.turno_disponible import TurnoDisponible
from app.models.usuario import Usuario
from app.models.usuario_role import UsuarioRole
from app.repositories.coloquio_repository import (
    ConvocatoriaAlumnoRepository,
    EvaluacionRepository,
    ReservaEvaluacionRepository,
    ResultadoEvaluacionRepository,
    TurnoDisponibleRepository,
)
from app.schemas.coloquio import (
    EvaluacionCreate,
    EvaluacionResponse,
    EvaluacionUpdate,
    MetricasResponse,
    TurnoDisponibleResponse,
)


class ColoquioService:
    def __init__(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        current_user_id: uuid.UUID,
    ) -> None:
        self._db = db
        self._tenant_id = tenant_id
        self._current_user_id = current_user_id
        self._evaluacion_repo = EvaluacionRepository(db, tenant_id)
        self._turno_repo = TurnoDisponibleRepository(db, tenant_id)
        self._reserva_repo = ReservaEvaluacionRepository(db, tenant_id)
        self._resultado_repo = ResultadoEvaluacionRepository(db, tenant_id)
        self._convocatoria_repo = ConvocatoriaAlumnoRepository(db, tenant_id)

    async def crear_convocatoria(self, data: EvaluacionCreate) -> EvaluacionResponse:
        evaluacion = await self._evaluacion_repo.create(
            tenant_id=self._tenant_id,
            materia_id=data.materia_id,
            cohorte_id=data.cohorte_id,
            tipo=data.tipo,
            instancia=data.instancia,
        )

        turnos = []
        for t in data.turnos:
            turno = await self._turno_repo.create(
                tenant_id=self._tenant_id,
                evaluacion_id=evaluacion.id,
                fecha=t.fecha,
                hora=t.hora,
                cupo_total=t.cupo_total,
                cupos_restantes=t.cupo_total,
            )
            turnos.append(turno)

        return EvaluacionResponse(
            id=evaluacion.id,
            tenant_id=evaluacion.tenant_id,
            materia_id=evaluacion.materia_id,
            cohorte_id=evaluacion.cohorte_id,
            tipo=evaluacion.tipo,
            instancia=evaluacion.instancia,
            turnos=[TurnoDisponibleResponse.model_validate(t) for t in turnos],
            created_at=evaluacion.created_at,
            updated_at=evaluacion.updated_at,
        )

    async def actualizar_convocatoria(
        self, evaluacion_id: uuid.UUID, data: EvaluacionUpdate
    ) -> EvaluacionResponse:
        try:
            evaluacion = await self._evaluacion_repo.get(evaluacion_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Convocatoria no encontrada",
            )

        update_kwargs = {}
        if data.tipo is not None:
            update_kwargs["tipo"] = data.tipo
        if data.instancia is not None:
            update_kwargs["instancia"] = data.instancia
        if update_kwargs:
            await self._evaluacion_repo.update(evaluacion_id, **update_kwargs)

        if data.turnos is not None:
            await self._turno_repo.delete_by_evaluacion(evaluacion_id)
            for t in data.turnos:
                await self._turno_repo.create(
                    tenant_id=self._tenant_id,
                    evaluacion_id=evaluacion_id,
                    fecha=t.fecha,
                    hora=t.hora,
                    cupo_total=t.cupo_total,
                    cupos_restantes=t.cupo_total,
                )

        evaluacion = await self._evaluacion_repo.get(evaluacion_id)
        turnos = await self._turno_repo.list_by_evaluacion(evaluacion_id)
        return EvaluacionResponse(
            id=evaluacion.id,
            tenant_id=evaluacion.tenant_id,
            materia_id=evaluacion.materia_id,
            cohorte_id=evaluacion.cohorte_id,
            tipo=evaluacion.tipo,
            instancia=evaluacion.instancia,
            turnos=[TurnoDisponibleResponse.model_validate(t) for t in turnos],
            created_at=evaluacion.created_at,
            updated_at=evaluacion.updated_at,
        )

    async def cerrar_convocatoria(self, evaluacion_id: uuid.UUID) -> None:
        try:
            await self._evaluacion_repo.get(evaluacion_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Convocatoria no encontrada",
            )
        await self._evaluacion_repo.soft_delete(evaluacion_id)

    async def listar_convocatorias(
        self,
        materia_id: uuid.UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[EvaluacionResponse], int, int]:
        items, total, pages = await self._evaluacion_repo.list_with_indicators(
            materia_id=materia_id,
            limit=limit,
            offset=offset,
        )
        results = []
        for e in items:
            turnos = await self._turno_repo.list_by_evaluacion(e.id)
            results.append(
                EvaluacionResponse(
                    id=e.id,
                    tenant_id=e.tenant_id,
                    materia_id=e.materia_id,
                    cohorte_id=e.cohorte_id,
                    tipo=e.tipo,
                    instancia=e.instancia,
                    turnos=[TurnoDisponibleResponse.model_validate(t) for t in turnos],
                    created_at=e.created_at,
                    updated_at=e.updated_at,
                )
            )
        return results, total, pages

    async def importar_padron(
        self, evaluacion_id: uuid.UUID, alumno_ids: list[uuid.UUID]
    ) -> dict:
        try:
            await self._evaluacion_repo.get(evaluacion_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Convocatoria no encontrada",
            )

        for alumno_id in alumno_ids:
            stmt = select(Usuario).where(
                Usuario.id == alumno_id,
                Usuario.tenant_id == self._tenant_id,
            )
            result = await self._db.execute(stmt)
            user = result.scalars().first()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Usuario con id={alumno_id} no encontrado",
                )

            has_alumno_role = await self._user_has_role(alumno_id, "ALUMNO")
            if not has_alumno_role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Usuario {alumno_id} no tiene rol ALUMNO",
                )

        count = 0
        for alumno_id in alumno_ids:
            await self._convocatoria_repo.upsert(evaluacion_id, alumno_id)
            count += 1

        return {"count": count}

    async def reservar_turno(
        self, evaluacion_id: uuid.UUID, turno_id: uuid.UUID, alumno_id: uuid.UUID
    ) -> ReservaEvaluacion:
        try:
            await self._evaluacion_repo.get(evaluacion_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Convocatoria no encontrada",
            )

        tiene_duplicado = await self._reserva_repo.has_activa_en_evaluacion(
            evaluacion_id, alumno_id
        )
        if tiene_duplicado:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya tiene una reserva activa en esta convocatoria",
            )

        filas = await self._turno_repo.decrementar_cupo(turno_id)
        if filas == 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No hay cupos disponibles en este turno",
            )

        reserva = await self._reserva_repo.create(
            tenant_id=self._tenant_id,
            evaluacion_id=evaluacion_id,
            alumno_id=alumno_id,
            turno_id=turno_id,
            fecha_hora=datetime.now(timezone.utc),
            estado=EstadoReserva.ACTIVA,
        )
        return reserva

    async def cancelar_reserva(self, reserva_id: uuid.UUID) -> ReservaEvaluacion:
        try:
            reserva = await self._reserva_repo.get(reserva_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva no encontrada",
            )

        if reserva.estado != EstadoReserva.ACTIVA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La reserva ya está cancelada",
            )

        await self._turno_repo.reincrementar_cupo(reserva.turno_id)
        return await self._reserva_repo.cancelar(reserva_id)

    async def registrar_resultado(
        self, evaluacion_id: uuid.UUID, alumno_id: uuid.UUID, nota_final: str
    ) -> ResultadoEvaluacion:
        try:
            await self._evaluacion_repo.get(evaluacion_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Convocatoria no encontrada",
            )

        await self._validar_alumno_convocado(evaluacion_id, alumno_id)

        return await self._resultado_repo.create(
            tenant_id=self._tenant_id,
            evaluacion_id=evaluacion_id,
            alumno_id=alumno_id,
            nota_final=nota_final,
        )

    async def registrar_resultados_batch(
        self, evaluacion_id: uuid.UUID, items: list[dict]
    ) -> dict:
        try:
            await self._evaluacion_repo.get(evaluacion_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Convocatoria no encontrada",
            )

        for item in items:
            await self._validar_alumno_convocado(
                evaluacion_id, item["alumno_id"]
            )

        batch_items = [
            {
                "tenant_id": self._tenant_id,
                "evaluacion_id": evaluacion_id,
                "alumno_id": item["alumno_id"],
                "nota_final": item["nota_final"],
            }
            for item in items
        ]
        resultados = await self._resultado_repo.create_batch(batch_items)
        return {"count": len(resultados)}

    async def obtener_metricas(self) -> MetricasResponse:
        total_alumnos_stmt = (
            select(func.count())
            .select_from(ConvocatoriaAlumno)
            .where(
                ConvocatoriaAlumno.tenant_id == self._tenant_id,
                ConvocatoriaAlumno.deleted_at.is_(None),
            )
        )
        total_alumnos = (await self._db.execute(total_alumnos_stmt)).scalar_one()

        instancias_activas_stmt = (
            select(func.count())
            .select_from(Evaluacion)
            .where(
                Evaluacion.tenant_id == self._tenant_id,
                Evaluacion.deleted_at.is_(None),
            )
        )
        instancias_activas = (await self._db.execute(instancias_activas_stmt)).scalar_one()

        reservas_activas_stmt = (
            select(func.count())
            .select_from(ReservaEvaluacion)
            .where(
                ReservaEvaluacion.tenant_id == self._tenant_id,
                ReservaEvaluacion.estado == EstadoReserva.ACTIVA,
                ReservaEvaluacion.deleted_at.is_(None),
            )
        )
        reservas_activas = (await self._db.execute(reservas_activas_stmt)).scalar_one()

        notas_registradas_stmt = (
            select(func.count())
            .select_from(ResultadoEvaluacion)
            .where(
                ResultadoEvaluacion.tenant_id == self._tenant_id,
                ResultadoEvaluacion.deleted_at.is_(None),
            )
        )
        notas_registradas = (await self._db.execute(notas_registradas_stmt)).scalar_one()

        return MetricasResponse(
            total_alumnos=total_alumnos,
            instancias_activas=instancias_activas,
            reservas_activas=reservas_activas,
            notas_registradas=notas_registradas,
        )

    async def _user_has_role(self, user_id: uuid.UUID, role_name: str) -> bool:
        stmt = (
            select(UsuarioRole)
            .join(Role, UsuarioRole.role_id == Role.id)
            .where(
                UsuarioRole.usuario_id == user_id,
                UsuarioRole.tenant_id == self._tenant_id,
                Role.name == role_name,
                Role.deleted_at.is_(None),
            )
        )
        result = await self._db.execute(stmt)
        return result.scalars().first() is not None

    async def _validar_alumno_convocado(
        self, evaluacion_id: uuid.UUID, alumno_id: uuid.UUID
    ) -> None:
        stmt = (
            select(ConvocatoriaAlumno)
            .where(
                ConvocatoriaAlumno.tenant_id == self._tenant_id,
                ConvocatoriaAlumno.evaluacion_id == evaluacion_id,
                ConvocatoriaAlumno.alumno_id == alumno_id,
                ConvocatoriaAlumno.deleted_at.is_(None),
            )
        )
        result = await self._db.execute(stmt)
        if result.scalars().first() is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El alumno no está habilitado para esta convocatoria",
            )
