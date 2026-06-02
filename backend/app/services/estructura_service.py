import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.repositories.carrera_repository import CarreraRepository
from app.repositories.cohorte_repository import CohorteRepository
from app.repositories.materia_repository import MateriaRepository
from app.schemas.carrera import CarreraCreate, CarreraUpdate
from app.schemas.cohorte import CohorteCreate, CohorteUpdate
from app.schemas.materia import MateriaCreate, MateriaUpdate


class CarreraService:
    def __init__(self, db: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._repo = CarreraRepository(db, tenant_id)
        self._db = db
        self._tenant_id = tenant_id

    async def create(self, body: CarreraCreate) -> Carrera:
        existing = await self._repo.get_by_codigo(body.codigo)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Carrera with this codigo already exists",
            )
        return await self._repo.create(
            tenant_id=self._tenant_id,
            codigo=body.codigo,
            nombre=body.nombre,
            descripcion=body.descripcion,
            duracion_anios=body.duracion_anios,
        )

    async def get(self, id: uuid.UUID) -> Carrera:
        try:
            return await self._repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Carrera not found",
            )

    async def list(self, limit: int = 20, offset: int = 0) -> tuple[list[Carrera], int, int]:
        items, total, pages = await self._repo.paginate(limit=limit, offset=offset)
        return list(items), total, pages

    async def update(self, id: uuid.UUID, body: CarreraUpdate) -> Carrera:
        try:
            await self._repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Carrera not found",
            )
        return await self._repo.update(
            id,
            nombre=body.nombre,
            descripcion=body.descripcion,
            duracion_anios=body.duracion_anios,
            is_active=body.is_active,
        )

    async def soft_delete(self, id: uuid.UUID) -> None:
        try:
            await self._repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Carrera not found",
            )
        cohorte_repo = CohorteRepository(self._db, self._tenant_id)
        active_count = await cohorte_repo.count_by_carrera(id, include_deleted=False)
        if active_count > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete carrera with existing cohorts",
            )
        await self._repo.soft_delete(id)


class CohorteService:
    def __init__(self, db: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._repo = CohorteRepository(db, tenant_id)
        self._carrera_repo = CarreraRepository(db, tenant_id)
        self._db = db
        self._tenant_id = tenant_id

    async def create(self, body: CohorteCreate) -> Cohorte:
        try:
            carrera = await self._carrera_repo.get(body.carrera_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Carrera not found",
            )
        if not carrera.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create cohorte for inactive carrera",
            )
        existing = await self._repo.get_by_nombre_and_carrera(body.nombre, body.carrera_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cohorte with this nombre already exists for this carrera",
            )
        return await self._repo.create(
            tenant_id=self._tenant_id,
            carrera_id=body.carrera_id,
            nombre=body.nombre,
            anio=body.anio,
        )

    async def get(self, id: uuid.UUID) -> Cohorte:
        try:
            return await self._repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cohorte not found",
            )

    async def list(
        self, limit: int = 20, offset: int = 0, carrera_id: uuid.UUID | None = None,
    ) -> tuple[list[Cohorte], int, int]:
        if carrera_id:
            items = await self._repo.list(carrera_id=carrera_id)
            total = len(items)
            pages = max(1, (total + limit - 1) // limit) if limit > 0 else 1
            return list(items), total, pages
        items, total, pages = await self._repo.paginate(limit=limit, offset=offset)
        return list(items), total, pages

    async def update(self, id: uuid.UUID, body: CohorteUpdate) -> Cohorte:
        try:
            await self._repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cohorte not found",
            )
        return await self._repo.update(
            id,
            nombre=body.nombre,
            anio=body.anio,
            is_active=body.is_active,
        )

    async def soft_delete(self, id: uuid.UUID) -> None:
        try:
            await self._repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cohorte not found",
            )
        await self._repo.soft_delete(id)


class MateriaService:
    def __init__(self, db: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._repo = MateriaRepository(db, tenant_id)
        self._db = db
        self._tenant_id = tenant_id

    async def create(self, body: MateriaCreate) -> Materia:
        existing = await self._repo.get_by_codigo(body.codigo)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Materia with this codigo already exists",
            )
        return await self._repo.create(
            tenant_id=self._tenant_id,
            carrera_id=body.carrera_id,
            codigo=body.codigo,
            nombre=body.nombre,
            descripcion=body.descripcion,
            carga_horaria=body.carga_horaria,
        )

    async def get(self, id: uuid.UUID) -> Materia:
        try:
            return await self._repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Materia not found",
            )

    async def list(
        self, limit: int = 20, offset: int = 0, carrera_id: uuid.UUID | None = None,
    ) -> tuple[list[Materia], int, int]:
        if carrera_id:
            items = await self._repo.list(carrera_id=carrera_id)
            total = len(items)
            pages = max(1, (total + limit - 1) // limit) if limit > 0 else 1
            return list(items), total, pages
        items, total, pages = await self._repo.paginate(limit=limit, offset=offset)
        return list(items), total, pages

    async def update(self, id: uuid.UUID, body: MateriaUpdate) -> Materia:
        try:
            await self._repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Materia not found",
            )
        return await self._repo.update(
            id,
            nombre=body.nombre,
            descripcion=body.descripcion,
            carga_horaria=body.carga_horaria,
            is_active=body.is_active,
        )

    async def soft_delete(self, id: uuid.UUID) -> None:
        try:
            await self._repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Materia not found",
            )
        await self._repo.soft_delete(id)
