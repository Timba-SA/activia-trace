import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://active_trace:active_trace@localhost:5432/active_trace_test")
os.environ.setdefault("SECRET_KEY", "abcd1234abcd1234abcd1234abcd1234")
os.environ.setdefault("ENCRYPTION_KEY", "abcd1234abcd1234abcd1234abcd1234")

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import func, select, update

from app.core.database import Base


@pytest.fixture(autouse=True)
def _register_models():
    import app.models.recovery_token  # noqa: F401
    import app.models.sesion  # noqa: F401
    import app.models.usuario  # noqa: F401


@pytest.fixture
async def tenant(db_session):
    from app.models.tenant import Tenant

    t = Tenant(
        id=uuid.uuid4(),
        name="Test Tenant",
        slug="test-tenant",
        code="TEST01",
        is_active=True,
    )
    db_session.add(t)
    await db_session.flush()
    return t


class TestUsuarioModel:
    async def test_create_usuario(self, db_session, tenant):
        from app.models.usuario import Usuario

        uid = uuid.uuid4()
        user = Usuario(
            id=uid,
            tenant_id=tenant.id,
            email="test@example.com",
            hashed_password="argon2hash",
        )
        db_session.add(user)
        await db_session.flush()

        assert user.id == uid
        assert user.tenant_id == tenant.id
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_2fa_enabled is False
        assert user.totp_secret is None
        assert user.created_at is not None

    async def test_usuario_soft_delete(self, db_session, tenant):
        from app.models.usuario import Usuario

        user = Usuario(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            email="softdelete@example.com",
            hashed_password="hash",
        )
        db_session.add(user)
        await db_session.flush()

        stmt = (
            update(Usuario)
            .where(Usuario.id == user.id)
            .values(deleted_at=func.now())
        )
        await db_session.execute(stmt)
        await db_session.flush()

        result = await db_session.execute(
            select(Usuario).where(Usuario.id == user.id, Usuario.deleted_at.is_(None))
        )
        assert result.scalars().first() is None


class TestSesionModel:
    async def test_create_sesion(self, db_session, tenant):
        from app.models.sesion import Sesion
        from app.models.usuario import Usuario

        user = Usuario(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            email="sesion_user@example.com",
            hashed_password="hash",
        )
        db_session.add(user)
        await db_session.flush()

        session = Sesion(
            id=uuid.uuid4(),
            user_id=user.id,
            refresh_token_hash="abc123hash",
            expires_at=None,
        )
        db_session.add(session)
        await db_session.flush()

        assert session.user_id == user.id
        assert session.refresh_token_hash == "abc123hash"
        assert session.is_revoked is False
        assert session.created_at is not None


class TestRecoveryTokenModel:
    async def test_create_recovery_token(self, db_session, tenant):
        from app.models.recovery_token import RecoveryToken
        from app.models.usuario import Usuario

        user = Usuario(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            email="recovery_user@example.com",
            hashed_password="hash",
        )
        db_session.add(user)
        await db_session.flush()

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        token = RecoveryToken(
            id=uuid.uuid4(),
            user_id=user.id,
            token_hash="recoveryhash123",
            expires_at=expires_at,
        )
        db_session.add(token)
        await db_session.flush()

        assert token.user_id == user.id
        assert token.token_hash == "recoveryhash123"
        assert token.used_at is None
        assert token.expires_at == expires_at
