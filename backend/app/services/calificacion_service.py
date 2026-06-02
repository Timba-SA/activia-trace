import csv
import hashlib
import io
import json
import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.calificacion_repository import CalificacionRepository
from app.repositories.umbral_materia_repository import UmbralMateriaRepository


def _compute_import_hash(rows: list[dict]) -> str:
    cleaned = [{k: v for k, v in e.items() if v is not None} for e in rows]
    raw = json.dumps(cleaned, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _detect_is_numeric(values: list[str]) -> bool:
    non_empty = [v for v in values if v and v.strip()]
    if not non_empty:
        return False
    for v in non_empty:
        try:
            float(v.strip())
        except (ValueError, TypeError):
            return False
    return True


async def _compute_aprobado(
    calificacion: str, es_numerica: bool, umbral,
) -> bool:
    if es_numerica:
        try:
            return float(calificacion) >= umbral.umbral_pct
        except (ValueError, TypeError):
            return False
    return calificacion in (umbral.valores_aprobados or [])


class CalificacionService:
    def __init__(self, db: AsyncSession, tenant_id: uuid.UUID, current_user_id: uuid.UUID) -> None:
        self._calificacion_repo = CalificacionRepository(db, tenant_id)
        self._umbral_repo = UmbralMateriaRepository(db, tenant_id)
        self._db = db
        self._tenant_id = tenant_id
        self._current_user_id = current_user_id

    async def preview_import(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID, file_content: bytes,
    ) -> dict:
        content_str = file_content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(content_str))

        fieldnames = reader.fieldnames or []
        known_columns = {"legajo", "nombre_completo", "email", "estado", "entrada_padron_id"}
        activity_columns = [c for c in fieldnames if c not in known_columns]

        if not activity_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No activity columns found in CSV",
            )

        rows = []
        all_values_by_col: dict[str, list[str]] = {col: [] for col in activity_columns}
        for row in reader:
            entrada_padron_id = row.get("entrada_padron_id", "").strip()
            legajo = row.get("legajo", "").strip()
            nombre_completo = row.get("nombre_completo", "").strip()
            valores = {}
            for col in activity_columns:
                val = row.get(col, "").strip()
                valores[col] = val
                all_values_by_col[col].append(val)
            rows.append({
                "entrada_padron_id": entrada_padron_id,
                "legajo": legajo,
                "nombre_completo": nombre_completo,
                "valores": valores,
            })

        if not rows:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No rows found in CSV",
            )

        columns = []
        for col in activity_columns:
            columns.append({
                "actividad_nombre": col,
                "es_numerica": _detect_is_numeric(all_values_by_col[col]),
            })

        preview_hash = _compute_import_hash(rows)

        return {
            "materia_id": str(materia_id),
            "cohorte_id": str(cohorte_id),
            "columns": columns,
            "rows": rows,
            "preview_hash": preview_hash,
        }

    async def confirm_import(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
        selected_activities: list[str], preview_hash: str, rows: list[dict],
    ) -> dict:
        computed_hash = _compute_import_hash(rows)
        if computed_hash != preview_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Preview data has changed. Please re-upload the file.",
            )

        umbral = await self._umbral_repo.get_by_materia(materia_id)
        if umbral is None:
            umbral = await self._umbral_repo.create(
                tenant_id=self._tenant_id,
                materia_id=materia_id,
                cohorte_id=cohorte_id,
                umbral_pct=60.0,
                valores_aprobados=["Aprobado", "Promocionado"],
            )

        columns = selected_activities
        column_is_numeric: dict[str, bool] = {}
        for col in columns:
            values_for_col = [
                row["valores"].get(col, "") for row in rows if row["valores"].get(col, "").strip()
            ]
            column_is_numeric[col] = _detect_is_numeric(values_for_col)

        calificaciones = []
        for row in rows:
            for col in columns:
                raw_val = row["valores"].get(col, "").strip()
                if not raw_val:
                    continue
                es_numerica = column_is_numeric[col]
                aprobado = await _compute_aprobado(raw_val, es_numerica, umbral)
                entrada_padron_id = None
                if row.get("entrada_padron_id"):
                    try:
                        entrada_padron_id = uuid.UUID(row["entrada_padron_id"])
                    except ValueError:
                        pass
                calificaciones.append({
                    "tenant_id": self._tenant_id,
                    "entrada_padron_id": entrada_padron_id,
                    "materia_id": materia_id,
                    "cohorte_id": cohorte_id,
                    "actividad_nombre": col,
                    "calificacion": raw_val,
                    "es_numerica": es_numerica,
                    "aprobado": aprobado,
                    "origen": "Importado",
                })

        created = await self._calificacion_repo.bulk_create(calificaciones)

        return {"total_creados": len(created)}

    async def list_calificaciones(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> tuple[list, int, int]:
        items = await self._calificacion_repo.list_by_materia_cohorte(materia_id, cohorte_id)
        total = len(items)
        pages = 1
        return list(items), total, pages
