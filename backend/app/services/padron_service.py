import csv
import hashlib
import io
import json
import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entrada_padron import EntradaPadron
from app.models.version_padron import VersionPadron
from app.repositories.padron_repository import EntradaPadronRepository, VersionPadronRepository


def _compute_preview_hash(entries: list[dict]) -> str:
    cleaned = [{k: v for k, v in e.items() if v is not None} for e in entries]
    raw = json.dumps(cleaned, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


class PadronService:
    def __init__(self, db: AsyncSession, tenant_id: uuid.UUID, current_user_id: uuid.UUID) -> None:
        self._version_repo = VersionPadronRepository(db, tenant_id)
        self._entrada_repo = EntradaPadronRepository(db, tenant_id)
        self._db = db
        self._tenant_id = tenant_id
        self._current_user_id = current_user_id

    async def preview_upload(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID, file_content: bytes,
    ) -> dict:
        content_str = file_content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(content_str))

        entries = []
        for row in reader:
            entries.append({
                "legajo": row.get("legajo", "").strip(),
                "nombre_completo": row.get("nombre_completo", "").strip(),
                "email": row.get("email", "").strip(),
                "estado": row.get("estado", "activo").strip(),
            })

        if not entries:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No entries found in file",
            )

        preview_hash = _compute_preview_hash(entries)

        return {
            "materia_id": str(materia_id),
            "cohorte_id": str(cohorte_id),
            "total_rows": len(entries),
            "entries": entries,
            "preview_hash": preview_hash,
        }

    async def confirm_upload(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
        preview_hash: str, entries: list[dict],
    ) -> dict:
        computed_hash = _compute_preview_hash(entries)
        if computed_hash != preview_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Preview data has changed. Please re-upload the file.",
            )

        await self._version_repo.deactivate_all_for_materia_cohorte(materia_id, cohorte_id)

        version = VersionPadron(
            tenant_id=self._tenant_id,
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            activa=True,
            creada_por=self._current_user_id,
        )
        self._db.add(version)
        await self._db.flush()

        entry_dicts = []
        for entry in entries:
            entry_dicts.append({
                "tenant_id": self._tenant_id,
                "version_padron_id": version.id,
                "legajo": entry["legajo"],
                "nombre_completo": entry["nombre_completo"],
                "email": entry["email"],
                "estado": entry.get("estado", "activo"),
            })

        created = await self._entrada_repo.bulk_create(entry_dicts)

        return {
            "version_id": str(version.id),
            "total_entradas": len(created),
            "activa": True,
        }

    async def get_active_padron(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> VersionPadron | None:
        return await self._version_repo.get_active(materia_id, cohorte_id)

    async def get_versiones(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> tuple[list[VersionPadron], int, int]:
        items = await self._version_repo.list_by_materia_cohorte(materia_id, cohorte_id)
        total = len(items)
        pages = 1
        return list(items), total, pages

    async def get_entradas(
        self, version_id: uuid.UUID,
    ) -> tuple[list[EntradaPadron], int, int]:
        items = await self._entrada_repo.list_by_version(version_id)
        total = len(items)
        pages = 1
        return list(items), total, pages
