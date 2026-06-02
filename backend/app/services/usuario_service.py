import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decrypt_value, encrypt_value
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import UsuarioUpdateRequest


class UsuarioService:
    def __init__(self, db: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._repo = UsuarioRepository(db, tenant_id)
        self._db = db
        self._tenant_id = tenant_id

    async def get(self, id: uuid.UUID) -> Usuario:
        try:
            return await self._repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario not found",
            )

    async def list(
        self,
        nombre: str | None = None,
        apellido: str | None = None,
        email: str | None = None,
        legajo: str | None = None,
        is_active: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Usuario], int, int]:
        return await self._repo.search_by_filters(
            nombre=nombre,
            apellido=apellido,
            email=email,
            legajo=legajo,
            is_active=is_active,
            limit=limit,
            offset=offset,
        )

    async def update(self, id: uuid.UUID, body: UsuarioUpdateRequest) -> Usuario:
        try:
            await self._repo.get(id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario not found",
            )

        kwargs = {}
        if body.nombre is not None:
            kwargs["nombre"] = body.nombre
        if body.apellido is not None:
            kwargs["apellido"] = body.apellido
        if body.telefono is not None:
            kwargs["telefono"] = body.telefono
        if body.direccion is not None:
            kwargs["direccion"] = body.direccion
        if body.fecha_nacimiento is not None:
            kwargs["fecha_nacimiento"] = body.fecha_nacimiento
        if body.is_active is not None:
            kwargs["is_active"] = body.is_active

        if body.dni is not None:
            kwargs["dni"] = encrypt_value(body.dni)
        if body.cuil is not None:
            kwargs["cuil"] = encrypt_value(body.cuil)
        if body.cbu is not None:
            kwargs["cbu"] = encrypt_value(body.cbu)

        if body.legajo is not None:
            existing = await self._repo.get_by_legajo(body.legajo)
            if existing and existing.id != id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Legajo already exists for this tenant",
                )
            kwargs["legajo"] = body.legajo

        return await self._repo.update(id, **kwargs)

    async def get_detalle(self, id: uuid.UUID, has_ver_pii: bool) -> dict:
        usuario = await self.get(id)
        data = {
            "id": usuario.id,
            "tenant_id": usuario.tenant_id,
            "email": usuario.email,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "legajo": usuario.legajo,
            "is_active": usuario.is_active,
            "created_at": usuario.created_at,
            "updated_at": usuario.updated_at,
            "dni": None,
            "cuil": None,
            "telefono": usuario.telefono,
            "direccion": usuario.direccion,
            "fecha_nacimiento": usuario.fecha_nacimiento,
            "cbu": None,
        }
        if has_ver_pii:
            if usuario.dni:
                data["dni"] = decrypt_value(usuario.dni)
            if usuario.cuil:
                data["cuil"] = decrypt_value(usuario.cuil)
            if usuario.cbu:
                data["cbu"] = decrypt_value(usuario.cbu)
        return data
