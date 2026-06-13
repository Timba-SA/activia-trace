import uuid
from collections.abc import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.recovery_token import RecoveryToken
from app.models.sesion import Sesion
from app.models.usuario import Usuario
from app.repositories.base import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID | None) -> None:
        super().__init__(session, tenant_id)

    @property
    def _model(self) -> type[Usuario]:
        return Usuario

    async def find_by_email(
        self, email: str, include_deleted: bool = False
    ) -> Usuario | None:
        stmt = select(Usuario).where(Usuario.email == email)
        stmt = self._apply_tenant_scope(stmt)
        stmt = self._apply_soft_delete_filter(stmt, include_deleted=include_deleted)
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def find_by_email_skip_tenant(
        self, email: str, include_deleted: bool = False
    ) -> Usuario | None:
        stmt = select(Usuario).where(Usuario.email == email)
        stmt = self._apply_soft_delete_filter(stmt, include_deleted=include_deleted)
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def update_password(self, user_id: uuid.UUID, hashed_password: str) -> None:
        stmt = (
            update(Usuario)
            .where(Usuario.id == user_id)
            .values(hashed_password=hashed_password)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def set_2fa_secret(self, user_id: uuid.UUID, encrypted_secret: str) -> None:
        stmt = (
            update(Usuario)
            .where(Usuario.id == user_id)
            .values(totp_secret=encrypted_secret)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def enable_2fa(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(Usuario)
            .where(Usuario.id == user_id)
            .values(is_2fa_enabled=True)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def clear_2fa(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(Usuario)
            .where(Usuario.id == user_id)
            .values(is_2fa_enabled=False, totp_secret=None)
        )
        await self._session.execute(stmt)
        await self._session.flush()


class SesionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self, user_id: uuid.UUID, refresh_token_hash: str, expires_at
    ) -> Sesion:
        sesion = Sesion(
            user_id=user_id,
            refresh_token_hash=refresh_token_hash,
            expires_at=expires_at,
        )
        self._session.add(sesion)
        await self._session.flush()
        return sesion

    async def find_by_hash(self, token_hash: str) -> Sesion | None:
        stmt = select(Sesion).where(Sesion.refresh_token_hash == token_hash)
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def revoke(self, sesion_id: uuid.UUID) -> None:
        stmt = (
            update(Sesion)
            .where(Sesion.id == sesion_id)
            .values(is_revoked=True)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(Sesion)
            .where(Sesion.user_id == user_id)
            .values(is_revoked=True)
        )
        await self._session.execute(stmt)
        await self._session.flush()


class RecoveryTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self, user_id: uuid.UUID, token_hash: str, expires_at
    ) -> RecoveryToken:
        token = RecoveryToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self._session.add(token)
        await self._session.flush()
        return token

    async def find_by_hash(self, token_hash: str) -> RecoveryToken | None:
        stmt = select(RecoveryToken).where(RecoveryToken.token_hash == token_hash)
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def mark_used(self, token_id: uuid.UUID) -> None:
        from datetime import datetime, timezone

        stmt = (
            update(RecoveryToken)
            .where(RecoveryToken.id == token_id)
            .values(used_at=datetime.now(timezone.utc))
        )
        await self._session.execute(stmt)
        await self._session.flush()
