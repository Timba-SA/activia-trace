"""Analisis service: atrasados detection, ranking, reports, monitors and export."""

import csv
import io
import uuid
from collections import defaultdict

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.analisis_repository import AnalisisRepository
from app.repositories.asignacion_repository import AsignacionRepository
from app.repositories.umbral_materia_repository import UmbralMateriaRepository


class AccessScope:
    """Resolved data scope for the current user based on roles and assignments."""

    def __init__(self, is_global: bool = False) -> None:
        self.is_global = is_global
        self.materia_ids: set[uuid.UUID] = set()
        self.cohorte_ids: set[uuid.UUID] = set()


class AnalisisService:
    """Business logic for all /api/analisis/* endpoints.

    Rule RN-06: un alumno está atrasado si tiene al menos una actividad
    faltante o con calificación por debajo del umbral.
    Rule RN-09: el ranking solo incluye alumnos con >= 1 actividad aprobada.
    """

    def __init__(self, db: AsyncSession, tenant_id: uuid.UUID, current_user_id: uuid.UUID) -> None:
        self._analisis_repo = AnalisisRepository(db, tenant_id)
        self._asignacion_repo = AsignacionRepository(db, tenant_id)
        self._umbral_repo = UmbralMateriaRepository(db, tenant_id)
        self._db = db
        self._tenant_id = tenant_id
        self._current_user_id = current_user_id

    async def resolve_scope(self, roles: list[str]) -> AccessScope:
        """Resolve data access scope from current user's active assignments.

        COORDINADOR and ADMIN get global (tenant-wide) scope.
        TUTOR and PROFESOR get scope restricted to their active materia/cohorte assignments.
        """
        if any(r in ("COORDINADOR", "ADMIN") for r in roles):
            return AccessScope(is_global=True)

        scope = AccessScope(is_global=False)
        asignaciones = await self._asignacion_repo.list_by_usuario(self._current_user_id)
        for a in asignaciones:
            if a.materia_id:
                scope.materia_ids.add(a.materia_id)
            if a.cohorte_id:
                scope.cohorte_ids.add(a.cohorte_id)
        return scope

    async def get_atrasados(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> dict:
        """Compute atrasados for a materia/cohorte (RN-06).

        Un alumno es atrasado si:
        - Tiene actividades faltantes (sin calificación)
        - O tiene calificaciones por debajo del umbral configurado
        """
        umbral = await self._umbral_repo.get_by_materia(materia_id)
        umbral_pct = umbral.umbral_pct if umbral else 60.0

        actividades = await self._analisis_repo.list_actividades(materia_id, cohorte_id)
        if not actividades:
            return {"items": [], "total": 0}

        alumnos = await self._analisis_repo.get_alumnos_por_materia_cohorte(materia_id, cohorte_id)
        calificaciones = await self._analisis_repo.get_calificaciones_por_materia_cohorte(
            materia_id, cohorte_id,
        )

        # Build lookup: (entrada_padron_id, actividad_nombre) -> calificacion
        calif_map: dict[tuple[uuid.UUID, str], dict] = {}
        for c in calificaciones:
            calif_map[(c.entrada_padron_id, c.actividad_nombre)] = {
                "calificacion": c.calificacion,
                "aprobado": c.aprobado,
                "es_numerica": c.es_numerica,
            }

        atrasados = []
        for alumno in alumnos:
            faltantes: list[str] = []
            bajo_umbral: list[str] = []
            aprobadas = 0
            for act in actividades:
                calif_data = calif_map.get((alumno.id, act))
                if calif_data is None:
                    faltantes.append(act)
                elif not calif_data["aprobado"]:
                    bajo_umbral.append(act)
                else:
                    aprobadas += 1

            if faltantes or bajo_umbral:
                atrasados.append({
                    "entrada_padron_id": alumno.id,
                    "legajo": alumno.legajo,
                    "nombre_completo": alumno.nombre_completo,
                    "actividades_faltantes": faltantes,
                    "actividades_bajo_umbral": bajo_umbral,
                    "total_actividades": len(actividades),
                    "aprobadas_count": aprobadas,
                })

        return {"items": atrasados, "total": len(atrasados)}

    async def get_ranking(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> dict:
        """Build ranking of approved activities (RN-09).

        Only includes alumnos with >= 1 approved activity, sorted descending.
        """
        aprobadas = await self._analisis_repo.get_aprobadas_count_por_alumno(
            materia_id, cohorte_id,
        )
        alumnos = await self._analisis_repo.get_alumnos_por_materia_cohorte(materia_id, cohorte_id)
        alumno_map = {a.id: a for a in alumnos}

        entries = []
        for row in aprobadas:
            pid = row["entrada_padron_id"]
            if row["aprobadas"] < 1:
                continue
            al = alumno_map.get(pid)
            entries.append({
                "entrada_padron_id": pid,
                "legajo": al.legajo if al else "",
                "nombre_completo": al.nombre_completo if al else "",
                "aprobadas_count": row["aprobadas"],
            })

        entries.sort(key=lambda e: e["aprobadas_count"], reverse=True)
        return {"items": entries, "total": len(entries)}

    async def get_reporte_rapido(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> dict:
        """Quick aggregate report by materia/cohorte."""
        atrasados_data = await self.get_atrasados(materia_id, cohorte_id)
        total_alumnos = (await self._analisis_repo.get_alumnos_por_materia_cohorte(
            materia_id, cohorte_id,
        ))
        total = len(total_alumnos)
        atrasados = atrasados_data["total"]
        evaluados = total - atrasados

        pendientes = await self._analisis_repo.get_pendientes_sin_calificar(
            materia_id, cohorte_id,
        )

        return {
            "materia_id": materia_id,
            "cohorte_id": cohorte_id,
            "total_alumnos": total,
            "evaluados": evaluados,
            "atrasados": atrasados,
            "sin_atrasos": evaluados,
            "pendientes_correccion": len(pendientes),
            "pct_atrasados": round(atrasados / total * 100, 1) if total else 0.0,
            "pct_evaluados": round(evaluados / total * 100, 1) if total else 0.0,
        }

    async def get_notas_finales(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
        grupos: dict[str, list[str]],
    ) -> dict:
        """Grouped final grades per alumno with average per group and overall."""
        actividades = await self._analisis_repo.list_actividades(materia_id, cohorte_id)
        calificaciones = await self._analisis_repo.get_calificaciones_por_materia_cohorte(
            materia_id, cohorte_id,
        )
        alumnos = await self._analisis_repo.get_alumnos_por_materia_cohorte(materia_id, cohorte_id)

        # Build lookup: (entrada_padron_id, actividad_nombre) -> calificacion
        calif_map: dict[tuple[uuid.UUID, str], dict] = {}
        for c in calificaciones:
            calif_map[(c.entrada_padron_id, c.actividad_nombre)] = {
                "calificacion": c.calificacion,
                "es_numerica": c.es_numerica,
            }

        entries = []
        for alumno in alumnos:
            grupo_vals: dict[str, list[float]] = defaultdict(list)
            for grupo_nombre, acts in grupos.items():
                for act in acts:
                    calif_data = calif_map.get((alumno.id, act))
                    if calif_data and calif_data["es_numerica"]:
                        try:
                            grupo_vals[grupo_nombre].append(float(calif_data["calificacion"]))
                        except (ValueError, TypeError):
                            pass

            grupos_result: dict[str, float | None] = {}
            all_vals: list[float] = []
            for gn in grupos:
                vals = grupo_vals.get(gn, [])
                grupos_result[gn] = round(sum(vals) / len(vals), 1) if vals else None
                all_vals.extend(vals)

            nota_final = round(sum(all_vals) / len(all_vals), 1) if all_vals else None

            entries.append({
                "entrada_padron_id": alumno.id,
                "legajo": alumno.legajo,
                "nombre_completo": alumno.nombre_completo,
                "grupos": grupos_result,
                "nota_final": nota_final,
            })

        return {"items": entries, "total": len(entries)}

    async def get_monitor(
        self,
        materia_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        alumno: str | None = None,
        email: str | None = None,
        actividad: str | None = None,
        min_completion: float | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> dict:
        """Monitor with filters and pagination."""
        offset = (page - 1) * limit

        rows, total = await self._analisis_repo.get_monitor_data(
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            alumno=alumno,
            email=email,
            actividad=actividad,
            min_completion=min_completion,
            from_date=None,
            to_date=None,
            offset=offset,
            limit=limit,
        )

        items = []
        for r in rows:
            items.append({
                "entrada_padron_id": r["entrada_padron_id"],
                "legajo": r["legajo"],
                "nombre_completo": r["nombre_completo"],
                "email": r["email"],
                "actividad": actividad or "",
                "calificacion": None,
                "aprobado": None,
                "es_numerica": None,
                "tiene_calificacion": False,
                "tiene_finalizacion": False,
            })

        pages = max(1, (total + limit - 1) // limit) if limit > 0 else 1
        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages,
        }

    async def get_entregas_sin_corregir(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> dict:
        """Detect entries with finalization but no matching calificacion."""
        pendientes = await self._analisis_repo.get_pendientes_sin_calificar(
            materia_id, cohorte_id,
        )

        items = []
        for p in pendientes:
            items.append({
                "entrada_padron_id": p["entrada_padron_id"],
                "legajo": p["legajo"],
                "nombre_completo": p["nombre_completo"],
                "email": p["email"],
                "actividad_nombre": "",
                "materia_id": materia_id,
                "cohorte_id": cohorte_id,
            })

        return {"items": items, "total": len(items)}

    async def export_entregas_sin_corregir_csv(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> str:
        """Generate CSV for entregas sin corregir."""
        data = await self.get_entregas_sin_corregir(materia_id, cohorte_id)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "entrada_padron_id", "legajo", "nombre_completo",
            "materia_id", "cohorte_id",
        ])
        for item in data["items"]:
            writer.writerow([
                str(item["entrada_padron_id"]),
                item["legajo"],
                item["nombre_completo"],
                str(item["materia_id"]),
                str(item["cohorte_id"]),
            ])
        return output.getvalue()
