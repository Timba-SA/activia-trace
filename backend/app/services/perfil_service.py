import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decrypt_value, encrypt_value
from app.repositories.auth_repository import UsuarioRepository
from app.schemas.usuario import PerfilOut, PerfilUpdate


class PerfilService:
    def __init__(self, db: AsyncSession, tenant_id: uuid.UUID, current_user_id: uuid.UUID) -> None:
        self._repo = UsuarioRepository(db, tenant_id)
        self._tenant_id = tenant_id
        self._current_user_id = current_user_id

    async def get_perfil(self) -> PerfilOut:
        usuario = await self._repo.get(self._current_user_id, skip_tenant_scope=True)
        return PerfilOut(
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            email=usuario.email,
            dni=decrypt_value(usuario.dni) if usuario.dni else None,
            cuil=decrypt_value(usuario.cuil) if usuario.cuil else None,
            telefono=usuario.telefono,
            direccion=usuario.direccion,
            fecha_nacimiento=str(usuario.fecha_nacimiento) if usuario.fecha_nacimiento else None,
            legajo=usuario.legajo,
            cbu=decrypt_value(usuario.cbu) if usuario.cbu else None,
        )

    async def update_perfil(self, data: PerfilUpdate) -> PerfilOut:
        usuario = await self._repo.get(self._current_user_id, skip_tenant_scope=True)
        kwargs = {}
        if data.nombre is not None:
            kwargs["nombre"] = data.nombre
        if data.apellido is not None:
            kwargs["apellido"] = data.apellido
        if data.email is not None:
            kwargs["email"] = data.email
        if data.telefono is not None:
            kwargs["telefono"] = data.telefono
        if data.direccion is not None:
            kwargs["direccion"] = data.direccion
        if data.legajo is not None:
            kwargs["legajo"] = data.legajo
        if data.fecha_nacimiento is not None:
            kwargs["fecha_nacimiento"] = data.fecha_nacimiento

        if data.dni is not None:
            kwargs["dni"] = encrypt_value(data.dni)
        if data.cbu is not None:
            kwargs["cbu"] = encrypt_value(data.cbu)

        if kwargs:
            usuario = await self._repo.update(
                self._current_user_id,
                skip_tenant_scope=True,
                **kwargs,
            )

        return PerfilOut(
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            email=usuario.email,
            dni=decrypt_value(usuario.dni) if usuario.dni else None,
            cuil=decrypt_value(usuario.cuil) if usuario.cuil else None,
            telefono=usuario.telefono,
            direccion=usuario.direccion,
            fecha_nacimiento=str(usuario.fecha_nacimiento) if usuario.fecha_nacimiento else None,
            legajo=usuario.legajo,
            cbu=decrypt_value(usuario.cbu) if usuario.cbu else None,
        )
