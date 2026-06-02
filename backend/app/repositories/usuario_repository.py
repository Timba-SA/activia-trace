import math
import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usuario import Usuario
from app.repositories.base import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id)

    @property
    def _model(self) -> type[Usuario]:
        return Usuario

    async def get_by_email(self, email: str) -> Usuario | None:
        stmt = select(Usuario).where(
            Usuario.email == email,
            Usuario.tenant_id == self._tenant_id,
            Usuario.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def get_by_legajo(self, legajo: str) -> Usuario | None:
        stmt = select(Usuario).where(
            Usuario.legajo == legajo,
            Usuario.tenant_id == self._tenant_id,
            Usuario.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def search_by_filters(
        self,
        nombre: str | None = None,
        apellido: str | None = None,
        email: str | None = None,
        legajo: str | None = None,
        is_active: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Usuario], int, int]:
        stmt = select(Usuario).where(
            Usuario.tenant_id == self._tenant_id,
            Usuario.deleted_at.is_(None),
        )
        if nombre:
            stmt = stmt.where(Usuario.nombre.ilike(f"%{nombre}%"))
        if apellido:
            stmt = stmt.where(Usuario.apellido.ilike(f"%{apellido}%"))
        if email:
            stmt = stmt.where(Usuario.email.ilike(f"%{email}%"))
        if legajo:
            stmt = stmt.where(Usuario.legajo.ilike(f"%{legajo}%"))
        if is_active is not None:
            stmt = stmt.where(Usuario.is_active == is_active)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())
        pages = max(1, math.ceil(total / limit)) if limit > 0 else 1
        return items, total, pages
