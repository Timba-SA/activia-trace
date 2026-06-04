import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.programa_materia_repository import ProgramaMateriaRepository
from app.schemas.programa_materia import (
    GenerarContenidoResponse,
    ProgramaMateriaCreate,
    ProgramaMateriaResponse,
    ProgramaMateriaUpdate,
)


class ProgramaMateriaService:
    def __init__(self, db: AsyncSession, tenant_id: uuid.UUID, current_user_id: uuid.UUID):
        self._db = db
        self._tenant_id = tenant_id
        self._current_user_id = current_user_id
        self._repo = ProgramaMateriaRepository(db, tenant_id)

    def _to_response(self, programa) -> ProgramaMateriaResponse:
        return ProgramaMateriaResponse(
            id=programa.id,
            tenant_id=programa.tenant_id,
            materia_id=programa.materia_id,
            carrera_id=programa.carrera_id,
            cohorte_id=programa.cohorte_id,
            titulo=programa.titulo,
            referencia_archivo=programa.referencia_archivo,
            contenido_html=programa.contenido_html,
            version=programa.version,
            activo=programa.activo,
            aprobado_en=programa.aprobado_en,
            created_at=programa.created_at,
            updated_at=programa.updated_at,
        )

    async def create(self, data: ProgramaMateriaCreate) -> ProgramaMateriaResponse:
        max_ver = await self._repo.get_max_version(
            data.materia_id, data.carrera_id, data.cohorte_id
        )
        new_version = max_ver + 1

        await self._repo.deactivate_all_for(
            data.materia_id, data.carrera_id, data.cohorte_id
        )

        programa = await self._repo.create(
            tenant_id=self._tenant_id,
            materia_id=data.materia_id,
            carrera_id=data.carrera_id,
            cohorte_id=data.cohorte_id,
            titulo=data.titulo,
            referencia_archivo=data.referencia_archivo,
            version=new_version,
            activo=True,
            aprobado_en=data.aprobado_en,
        )
        return self._to_response(programa)

    async def update(self, id: uuid.UUID, data: ProgramaMateriaUpdate) -> ProgramaMateriaResponse:
        kwargs = {}
        if data.titulo is not None:
            kwargs["titulo"] = data.titulo
        if data.referencia_archivo is not None:
            kwargs["referencia_archivo"] = data.referencia_archivo
        if data.contenido_html is not None:
            kwargs["contenido_html"] = data.contenido_html
        if data.aprobado_en is not None:
            kwargs["aprobado_en"] = data.aprobado_en
        programa = await self._repo.update(id, **kwargs)
        return self._to_response(programa)

    async def deactivate(self, id: uuid.UUID) -> None:
        try:
            await self._repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Programa no encontrado",
            )
        await self._repo.update(id, activo=False)

    async def list(
        self,
        filters: dict,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[ProgramaMateriaResponse], int, int]:
        items, total, pages = await self._repo.list_filters(
            materia_id=filters.get("materia_id"),
            carrera_id=filters.get("carrera_id"),
            cohorte_id=filters.get("cohorte_id"),
            activo=filters.get("activo"),
            incluir_inactivos=filters.get("incluir_inactivos", False),
            limit=limit,
            offset=offset,
        )
        results = [self._to_response(p) for p in items]
        return results, total, pages

    async def get_by_id(self, id: uuid.UUID) -> ProgramaMateriaResponse:
        try:
            programa = await self._repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Programa no encontrado",
            )
        return self._to_response(programa)

    async def generar_contenido(self, id: uuid.UUID) -> GenerarContenidoResponse:
        try:
            programa = await self._repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Programa no encontrado",
            )

        if not programa.activo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Programa no encontrado",
            )

        html = (
            f"<h2>{programa.titulo}</h2>\n"
            f"<p>Materia ID: {programa.materia_id}</p>\n"
            f"<p>Carrera ID: {programa.carrera_id}</p>\n"
            f"<p>Versión: {programa.version}</p>\n"
        )
        if programa.referencia_archivo:
            html += f'<p><a href="{programa.referencia_archivo}">Archivo de referencia</a></p>\n'
        if programa.contenido_html:
            html += programa.contenido_html

        return GenerarContenidoResponse(contenido_html=html)
