import os
import asyncio
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import pyotp
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import close_db_engine
from tests.db_utils import drop_enum_types
from app.core.security import (
    create_access_token,
    create_temp_token,
    encrypt_value,
    generate_refresh_token,
    hash_password,
    verify_password,
)
from app.models.recovery_token import RecoveryToken
from app.models.sesion import Sesion
from app.models.tenant import Tenant
from app.models.usuario import Usuario

pytestmark = pytest.mark.asyncio

_db_host = os.environ.get('POSTGRES_HOST', 'localhost')
DB_URL = f"postgresql+asyncpg://active_trace:active_trace@{_db_host}:5432/active_trace_test"


async def _setup_db():
    from app.core.database import Base
    eng = create_async_engine(DB_URL, echo=False)
    async with eng.begin() as conn:
        await drop_enum_types(conn)
        await conn.run_sync(Base.metadata.create_all)
    await eng.dispose()


async def _teardown_db():
    from app.core.database import Base
    eng = create_async_engine(DB_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()
    await close_db_engine()


TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


async def _seed_tenant(eng):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        tenant = Tenant(
            id=TENANT_ID,
            name="Test Tenant",
            slug="test-tenant",
            code="TEST",
        )
        session.add(tenant)
        await session.commit()


async def _seed_user(eng, email, password="testpass123", is_active=True, is_2fa_enabled=False, totp_secret=None):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        hashed = hash_password(password)
        user = Usuario(
            id=uuid.uuid4(),
            tenant_id=TENANT_ID,
            email=email,
            hashed_password=hashed,
            is_active=is_active,
            is_2fa_enabled=is_2fa_enabled,
            totp_secret=totp_secret,
        )
        session.add(user)
        await session.commit()
        return user


async def _make_app():
    from app.main import create_app
    app = create_app()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


class TestLogin:
    async def test_login_valid_credentials(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            await _seed_user(eng, "test@example.com")
            async with await _make_app() as client:
                response = await client.post("/api/auth/login", json={
                    "email": "test@example.com",
                    "password": "testpass123",
                })
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"
            assert data["expires_in"] == 900
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_login_invalid_password(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            await _seed_user(eng, "test2@example.com")
            async with await _make_app() as client:
                response = await client.post("/api/auth/login", json={
                    "email": "test2@example.com",
                    "password": "wrongpass",
                })
            assert response.status_code == 401
            assert "Invalid" in response.json()["detail"]
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_login_nonexistent_email(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            async with await _make_app() as client:
                response = await client.post("/api/auth/login", json={
                    "email": "nobody@example.com",
                    "password": "testpass123",
                })
            assert response.status_code == 401
            assert "Invalid" in response.json()["detail"]
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_login_inactive_user(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            await _seed_user(eng, "inactive@example.com", is_active=False)
            async with await _make_app() as client:
                response = await client.post("/api/auth/login", json={
                    "email": "inactive@example.com",
                    "password": "testpass123",
                })
            assert response.status_code == 401
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_login_with_2fa_returns_temp_token(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            import pyotp
            secret = pyotp.random_base32()
            await _seed_user(eng, "2fa@example.com", is_2fa_enabled=True, totp_secret=encrypt_value(secret))
            async with await _make_app() as client:
                response = await client.post("/api/auth/login", json={
                    "email": "2fa@example.com",
                    "password": "testpass123",
                })
            assert response.status_code == 200
            data = response.json()
            assert "temp_token" in data
            assert data["requires_2fa"] is True
            assert "access_token" not in data
        finally:
            await _teardown_db()
            await eng.dispose()


class TestLogin2FA:
    async def test_2fa_login_valid_code(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            secret = pyotp.random_base32()
            user = await _seed_user(eng, "2fa2@example.com", is_2fa_enabled=True, totp_secret=encrypt_value(secret))
            totp = pyotp.TOTP(secret)
            code = totp.now()
            temp_token = create_temp_token(user.id, TENANT_ID)
            async with await _make_app() as client:
                response = await client.post("/api/auth/login/2fa", json={
                    "temp_token": temp_token,
                    "code": code,
                })
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_2fa_login_invalid_code(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            secret = pyotp.random_base32()
            user = await _seed_user(eng, "2fa3@example.com", is_2fa_enabled=True, totp_secret=encrypt_value(secret))
            temp_token = create_temp_token(user.id, TENANT_ID)
            async with await _make_app() as client:
                response = await client.post("/api/auth/login/2fa", json={
                    "temp_token": temp_token,
                    "code": "000000",
                })
            assert response.status_code == 401
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_2fa_login_nonexistent_user(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            temp_token = create_temp_token(uuid.uuid4(), TENANT_ID)
            async with await _make_app() as client:
                response = await client.post("/api/auth/login/2fa", json={
                    "temp_token": temp_token,
                    "code": "123456",
                })
            assert response.status_code == 401
        finally:
            await _teardown_db()
            await eng.dispose()


class TestRefreshToken:
    async def test_successful_refresh(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                hashed = hash_password("testpass123")
                user = Usuario(id=uuid.uuid4(), tenant_id=TENANT_ID, email="refresh@example.com", hashed_password=hashed, is_active=True)
                session.add(user)
                await session.flush()
                raw, hash_val = generate_refresh_token()
                expires_at = datetime.now(timezone.utc) + timedelta(days=7)
                sesion = Sesion(user_id=user.id, refresh_token_hash=hash_val, expires_at=expires_at)
                session.add(sesion)
                await session.commit()

            async with await _make_app() as client:
                response = await client.post("/api/auth/refresh", json={"refresh_token": raw})
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data

            async with factory() as session:
                result = await session.execute(select(Sesion).where(Sesion.user_id == user.id))
                old = result.scalars().first()
                assert old is not None
                assert old.is_revoked is True
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_refresh_with_invalid_token(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            async with await _make_app() as client:
                response = await client.post("/api/auth/refresh", json={"refresh_token": "invalidtoken"})
            assert response.status_code == 401
        finally:
            await _teardown_db()
            await eng.dispose()


class TestForgotPassword:
    async def test_forgot_password_existing_user(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            await _seed_user(eng, "forgot@example.com")
            async with await _make_app() as client:
                response = await client.post("/api/auth/forgot", json={"email": "forgot@example.com"})
            assert response.status_code == 200
            data = response.json()
            assert "token" in data
            assert data["expires_in_minutes"] == 15
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_forgot_password_nonexistent_email(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            async with await _make_app() as client:
                response = await client.post("/api/auth/forgot", json={"email": "nobody@example.com"})
            assert response.status_code == 200
            assert "token" not in response.json()
        finally:
            await _teardown_db()
            await eng.dispose()


class TestResetPassword:
    async def test_successful_reset(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                hashed = hash_password("testpass123")
                user = Usuario(id=uuid.uuid4(), tenant_id=TENANT_ID, email="reset@example.com", hashed_password=hashed, is_active=True)
                session.add(user)
                await session.flush()
                raw_token = secrets.token_hex(32)
                token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
                expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
                rt = RecoveryToken(user_id=user.id, token_hash=token_hash, expires_at=expires_at)
                session.add(rt)
                await session.commit()

            async with await _make_app() as client:
                response = await client.post("/api/auth/reset", json={
                    "token": raw_token, "email": "reset@example.com", "new_password": "newpass12345",
                })
            assert response.status_code == 200

            async with factory() as session:
                result = await session.execute(select(Usuario).where(Usuario.id == user.id))
                updated = result.scalars().first()
                assert verify_password("newpass12345", updated.hashed_password)
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_reset_with_short_password(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            async with await _make_app() as client:
                response = await client.post("/api/auth/reset", json={
                    "token": "sometoken", "email": "test@example.com", "new_password": "short",
                })
            assert response.status_code == 422
        finally:
            await _teardown_db()
            await eng.dispose()


class TestForgotResetFlow:
    async def test_full_forgot_reset_flow(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            await _seed_user(eng, "flow@example.com")
            async with await _make_app() as client:
                resp = await client.post("/api/auth/forgot", json={"email": "flow@example.com"})
                assert resp.status_code == 200
                token = resp.json().get("token")
                assert token is not None

                resp2 = await client.post("/api/auth/reset", json={
                    "token": token, "email": "flow@example.com", "new_password": "newpass12345",
                })
                assert resp2.status_code == 200

                resp3 = await client.post("/api/auth/login", json={
                    "email": "flow@example.com", "password": "newpass12345",
                })
                assert resp3.status_code == 200
                assert "access_token" in resp3.json()

                resp4 = await client.post("/api/auth/login", json={
                    "email": "flow@example.com", "password": "testpass123",
                })
                assert resp4.status_code == 401
        finally:
            await _teardown_db()
            await eng.dispose()


class TestSchemaValidation:
    async def test_login_request_extra_fields_rejected(self):
        from pydantic import ValidationError
        from app.schemas.auth import LoginRequest
        with pytest.raises(ValidationError):
            LoginRequest(email="test@example.com", password="pass", extra_field="bad")

    async def test_token_response_extra_fields_rejected(self):
        from pydantic import ValidationError
        from app.schemas.auth import TokenResponse
        with pytest.raises(ValidationError):
            TokenResponse(access_token="x", refresh_token="y", extra_field="bad")

    async def test_reset_password_short_password_rejected(self):
        from pydantic import ValidationError
        from app.schemas.auth import ResetPasswordRequest
        with pytest.raises(ValidationError):
            ResetPasswordRequest(token="x", email="test@example.com", new_password="short")


class TestFraudDetection:
    async def test_reuse_revoked_refresh_triggers_fraud(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            await _seed_user(eng, "fraud@example.com")
            async with await _make_app() as client:
                resp = await client.post("/api/auth/login", json={
                    "email": "fraud@example.com", "password": "testpass123",
                })
                assert resp.status_code == 200
                refresh_1 = resp.json()["refresh_token"]

                resp2 = await client.post("/api/auth/refresh", json={"refresh_token": refresh_1})
                assert resp2.status_code == 200
                refresh_2 = resp2.json()["refresh_token"]

                resp3 = await client.post("/api/auth/refresh", json={"refresh_token": refresh_1})
                assert resp3.status_code == 401
                assert "all sessions" in resp3.json()["detail"].lower()

                resp4 = await client.post("/api/auth/refresh", json={"refresh_token": refresh_2})
                assert resp4.status_code == 401
        finally:
            await _teardown_db()
            await eng.dispose()


class TestLogout:
    async def test_logout_revokes_session(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            await _seed_user(eng, "logout@example.com")
            async with await _make_app() as client:
                resp = await client.post("/api/auth/login", json={
                    "email": "logout@example.com", "password": "testpass123",
                })
                assert resp.status_code == 200
                data = resp.json()
                access_token = data["access_token"]
                refresh_token = data["refresh_token"]

                resp2 = await client.post("/api/auth/logout", json={"refresh_token": refresh_token},
                    headers={"Authorization": f"Bearer {access_token}"})
                assert resp2.status_code == 200

                resp3 = await client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
                assert resp3.status_code == 401
        finally:
            await _teardown_db()
            await eng.dispose()


class TestRecoveryToken:
    async def test_reset_with_used_recovery_token_fails(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            await _seed_user(eng, "usedrec@example.com")
            async with await _make_app() as client:
                resp = await client.post("/api/auth/forgot", json={"email": "usedrec@example.com"})
                assert resp.status_code == 200
                token = resp.json()["token"]

                resp2 = await client.post("/api/auth/reset", json={
                    "token": token, "email": "usedrec@example.com", "new_password": "newpass12345",
                })
                assert resp2.status_code == 200

                resp3 = await client.post("/api/auth/reset", json={
                    "token": token, "email": "usedrec@example.com", "new_password": "another45678",
                })
                assert resp3.status_code == 400
                assert "already used" in resp3.json()["detail"].lower()
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_reset_with_expired_recovery_token_fails(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                hashed = hash_password("testpass123")
                user = Usuario(id=uuid.uuid4(), tenant_id=TENANT_ID, email="expiredrt@example.com", hashed_password=hashed, is_active=True)
                session.add(user)
                await session.flush()
                raw_token = secrets.token_hex(32)
                token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
                expires_at = datetime.now(timezone.utc) - timedelta(minutes=5)
                rt = RecoveryToken(user_id=user.id, token_hash=token_hash, expires_at=expires_at)
                session.add(rt)
                await session.commit()

            async with await _make_app() as client:
                resp = await client.post("/api/auth/reset", json={
                    "token": raw_token, "email": "expiredrt@example.com", "new_password": "newpass12345",
                })
                assert resp.status_code == 400
                assert "expired" in resp.json()["detail"].lower()
        finally:
            await _teardown_db()
            await eng.dispose()


class TestRateLimiting:
    async def test_rate_limiting_blocks_after_5_attempts(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            await _seed_user(eng, "ratelimit@example.com")
            async with await _make_app() as client:
                for _ in range(5):
                    resp = await client.post("/api/auth/login", json={
                        "email": "ratelimit@example.com", "password": "wrongpass",
                    })
                    assert resp.status_code == 401

                resp6 = await client.post("/api/auth/login", json={
                    "email": "ratelimit@example.com", "password": "wrongpass",
                })
                assert resp6.status_code == 429
        finally:
            await _teardown_db()
            await eng.dispose()


class TestGetCurrentUser:
    async def test_valid_token_authenticates(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            await _seed_user(eng, "guv@example.com")
            async with await _make_app() as client:
                resp = await client.post("/api/auth/login", json={
                    "email": "guv@example.com", "password": "testpass123",
                })
                assert resp.status_code == 200
                at = resp.json()["access_token"]
                rt = resp.json()["refresh_token"]

                resp2 = await client.post("/api/auth/logout", json={"refresh_token": rt},
                    headers={"Authorization": f"Bearer {at}"})
                assert resp2.status_code == 200
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_expired_token_rejected(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng, "et@example.com")
            expired = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": []},
                expire_minutes=-1,
            )
            await asyncio.sleep(0.1)
            async with await _make_app() as client:
                resp = await client.post("/api/auth/logout", json={"refresh_token": "x"},
                    headers={"Authorization": f"Bearer {expired}"})
                assert resp.status_code == 401
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_invalid_signature_rejected(self):
        from jose import jwt as jose_jwt
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            bad_token = jose_jwt.encode(
                {"sub": str(uuid.uuid4()), "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
                "wrongsecretkey1234567890123456",
                algorithm="HS256",
            )
            async with await _make_app() as client:
                resp = await client.post("/api/auth/logout", json={"refresh_token": "x"},
                    headers={"Authorization": f"Bearer {bad_token}"})
                assert resp.status_code == 401
        finally:
            await _teardown_db()
            await eng.dispose()


class Test2FAEnrollDisable:
    async def test_enroll_2fa_returns_secret(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            await _seed_user(eng, "enroll2fa@example.com")
            async with await _make_app() as client:
                resp = await client.post("/api/auth/login", json={
                    "email": "enroll2fa@example.com", "password": "testpass123",
                })
                assert resp.status_code == 200
                at = resp.json()["access_token"]

                resp2 = await client.post("/api/auth/2fa/enroll", json={},
                    headers={"Authorization": f"Bearer {at}"})
                assert resp2.status_code == 200
                data = resp2.json()
                assert "secret" in data
                assert "provisioning_uri" in data
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_enroll_when_already_enabled_raises_conflict(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            secret = pyotp.random_base32()
            user = await _seed_user(eng, "already2fa@example.com", is_2fa_enabled=True, totp_secret=encrypt_value(secret))
            async with await _make_app() as client:
                resp = await client.post("/api/auth/login", json={
                    "email": "already2fa@example.com", "password": "testpass123",
                })
                assert resp.status_code == 200
                assert resp.json()["requires_2fa"] is True
                temp_token = resp.json()["temp_token"]

                totp = pyotp.TOTP(secret)
                resp2 = await client.post("/api/auth/login/2fa", json={
                    "temp_token": temp_token, "code": totp.now(),
                })
                assert resp2.status_code == 200
                at = resp2.json()["access_token"]

                resp3 = await client.post("/api/auth/2fa/enroll", json={},
                    headers={"Authorization": f"Bearer {at}"})
                assert resp3.status_code == 409
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_disable_2fa_clears_secret(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            secret = pyotp.random_base32()
            user = await _seed_user(eng, "disable2fa@example.com", is_2fa_enabled=True, totp_secret=encrypt_value(secret))
            async with await _make_app() as client:
                resp = await client.post("/api/auth/login", json={
                    "email": "disable2fa@example.com", "password": "testpass123",
                })
                assert resp.status_code == 200
                assert resp.json()["requires_2fa"] is True
                temp_token = resp.json()["temp_token"]

                totp = pyotp.TOTP(secret)
                resp2 = await client.post("/api/auth/login/2fa", json={
                    "temp_token": temp_token, "code": totp.now(),
                })
                assert resp2.status_code == 200
                at = resp2.json()["access_token"]

                resp3 = await client.post("/api/auth/2fa/disable",
                    headers={"Authorization": f"Bearer {at}"})
                assert resp3.status_code == 200
                assert resp3.json()["message"] == "2FA disabled successfully"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_full_enrollment_flow(self):
        """Enroll → verify with TOTP → login now requires 2FA → login/2fa works"""
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            await _seed_user(eng, "full2fa@example.com")
            async with await _make_app() as client:
                resp = await client.post("/api/auth/login", json={
                    "email": "full2fa@example.com", "password": "testpass123",
                })
                assert resp.status_code == 200
                data = resp.json()
                assert "access_token" in data
                assert "requires_2fa" not in data
                at = data["access_token"]

                resp2 = await client.post("/api/auth/2fa/enroll", json={},
                    headers={"Authorization": f"Bearer {at}"})
                assert resp2.status_code == 200
                secret = resp2.json()["secret"]

                totp = pyotp.TOTP(secret)
                resp3 = await client.post("/api/auth/2fa/verify", json={"code": totp.now()},
                    headers={"Authorization": f"Bearer {at}"})
                assert resp3.status_code == 200
                assert resp3.json()["message"] == "2FA enabled successfully"

                resp4 = await client.post("/api/auth/login", json={
                    "email": "full2fa@example.com", "password": "testpass123",
                })
                assert resp4.status_code == 200
                assert resp4.json()["requires_2fa"] is True
                temp_token = resp4.json()["temp_token"]

                resp5 = await client.post("/api/auth/login/2fa", json={
                    "temp_token": temp_token, "code": totp.now(),
                })
                assert resp5.status_code == 200
                assert "access_token" in resp5.json()
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_disable_2fa_allows_login_without_2fa(self):
        """Disable 2FA → login without 2FA works again"""
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            secret = pyotp.random_base32()
            user = await _seed_user(eng, "disablelogin@example.com", is_2fa_enabled=True, totp_secret=encrypt_value(secret))
            async with await _make_app() as client:
                resp = await client.post("/api/auth/login", json={
                    "email": "disablelogin@example.com", "password": "testpass123",
                })
                assert resp.status_code == 200
                assert resp.json()["requires_2fa"] is True
                temp_token = resp.json()["temp_token"]

                totp = pyotp.TOTP(secret)
                resp2 = await client.post("/api/auth/login/2fa", json={
                    "temp_token": temp_token, "code": totp.now(),
                })
                assert resp2.status_code == 200
                at = resp2.json()["access_token"]

                resp3 = await client.post("/api/auth/2fa/disable",
                    headers={"Authorization": f"Bearer {at}"})
                assert resp3.status_code == 200

                resp4 = await client.post("/api/auth/login", json={
                    "email": "disablelogin@example.com", "password": "testpass123",
                })
                assert resp4.status_code == 200
                data = resp4.json()
                assert "access_token" in data
                assert "requires_2fa" not in data
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_disable_2fa_when_not_enabled_raises_error(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            await _seed_user(eng, "no2fa@example.com")
            async with await _make_app() as client:
                resp = await client.post("/api/auth/login", json={
                    "email": "no2fa@example.com", "password": "testpass123",
                })
                assert resp.status_code == 200
                at = resp.json()["access_token"]

                resp2 = await client.post("/api/auth/2fa/disable",
                    headers={"Authorization": f"Bearer {at}"})
                assert resp2.status_code == 400
                assert "not enabled" in resp2.json()["detail"].lower()
        finally:
            await _teardown_db()
            await eng.dispose()


class TestIdentityImmutability:
    async def test_2fa_operations_scoped_to_jwt_user(self):
        """2FA operations affect only the JWT-authenticated user, not other users"""
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            await _seed_user(eng, "immuta@example.com")
            await _seed_user(eng, "immutb@example.com")

            async with await _make_app() as client:
                resp = await client.post("/api/auth/login", json={
                    "email": "immuta@example.com", "password": "testpass123",
                })
                assert resp.status_code == 200
                at_a = resp.json()["access_token"]

                resp2 = await client.post("/api/auth/2fa/enroll", json={},
                    headers={"Authorization": f"Bearer {at_a}"})
                assert resp2.status_code == 200
                secret = resp2.json()["secret"]

                totp = pyotp.TOTP(secret)
                resp3 = await client.post("/api/auth/2fa/verify", json={"code": totp.now()},
                    headers={"Authorization": f"Bearer {at_a}"})
                assert resp3.status_code == 200

                resp4 = await client.post("/api/auth/login", json={
                    "email": "immutb@example.com", "password": "testpass123",
                })
                assert resp4.status_code == 200
                data = resp4.json()
                assert "access_token" in data
                assert "requires_2fa" not in data
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_query_params_cannot_override_jwt_identity(self):
        """Query params in request cannot override JWT identity"""
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            await _seed_user(eng, "queryid@example.com")
            async with await _make_app() as client:
                resp = await client.post("/api/auth/login", json={
                    "email": "queryid@example.com", "password": "testpass123",
                })
                assert resp.status_code == 200
                at = resp.json()["access_token"]

                resp2 = await client.post("/api/auth/logout?user_id=00000000-0000-0000-0000-000000000099",
                    json={"refresh_token": "invalid"},
                    headers={"Authorization": f"Bearer {at}"})
                assert resp2.status_code == 200
        finally:
            await _teardown_db()
            await eng.dispose()
