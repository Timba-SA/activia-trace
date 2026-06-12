"""Integration tests for perfil (self-profile) endpoints."""
import os
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base, close_db_engine
from app.core.security import create_access_token, hash_password
from app.models.tenant import Tenant
from app.models.usuario import Usuario

pytestmark = pytest.mark.asyncio

_db_host = os.environ.get('POSTGRES_HOST', 'localhost')
DB_URL = f"postgresql+asyncpg://active_trace:active_trace@{_db_host}:5432/active_trace_test"
TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


async def _setup_db():
    eng = create_async_engine(DB_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await eng.dispose()


async def _teardown_db():
    eng = create_async_engine(DB_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()
    await close_db_engine()


async def _make_client():
    from app.main import create_app
    app = create_app()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


class TestPerfil:
    async def test_get_perfil_returns_own_profile(self):
        await close_db_engine()
        eng = create_async_engine(DB_URL, echo=False)
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        factory = async_sessionmaker(eng, expire_on_commit=False)

        async with factory() as session:
            tenant = Tenant(id=TENANT_ID, name="Test", slug="test-tenant", code="TEST")
            session.add(tenant)
            user = Usuario(
                id=uuid.uuid4(),
                tenant_id=TENANT_ID,
                email="user@test.com",
                hashed_password=hash_password("testpass123"),
                nombre="Juan",
                apellido="Pérez",
                legajo="L123",
                is_active=True,
            )
            session.add(user)
            await session.commit()
            user_id = user.id

        token = create_access_token({"sub": str(user_id), "tenant_id": str(TENANT_ID), "roles": []})
        headers = {"Authorization": f"Bearer {token}"}

        client = await _make_client()
        try:
            resp = await client.get("/api/perfil", headers=headers)
            assert resp.status_code == 200, resp.text
            data = resp.json()
            assert data["nombre"] == "Juan"
            assert data["apellido"] == "Pérez"
            assert data["legajo"] == "L123"
            assert data["email"] == "user@test.com"
        finally:
            await client.aclose()

        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await eng.dispose()

    async def test_get_perfil_without_auth_returns_401(self):
        await close_db_engine()
        await _setup_db()
        client = await _make_client()
        try:
            resp = await client.get("/api/perfil")
            assert resp.status_code == 401
        finally:
            await client.aclose()
        await _teardown_db()

    async def test_update_perfil_editable_fields(self):
        await close_db_engine()
        eng = create_async_engine(DB_URL, echo=False)
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        factory = async_sessionmaker(eng, expire_on_commit=False)

        async with factory() as session:
            tenant = Tenant(id=TENANT_ID, name="Test", slug="test-tenant", code="TEST")
            session.add(tenant)
            user = Usuario(
                id=uuid.uuid4(),
                tenant_id=TENANT_ID,
                email="user@test.com",
                hashed_password=hash_password("testpass123"),
                nombre="Juan",
                apellido="Pérez",
                is_active=True,
            )
            session.add(user)
            await session.commit()
            user_id = user.id

        token = create_access_token({"sub": str(user_id), "tenant_id": str(TENANT_ID), "roles": []})
        headers = {"Authorization": f"Bearer {token}"}

        client = await _make_client()
        try:
            resp = await client.patch(
                "/api/perfil",
                json={"nombre": "Carlos", "apellido": "García", "telefono": "123456789"},
                headers=headers,
            )
            assert resp.status_code == 200, resp.text
            data = resp.json()
            assert data["nombre"] == "Carlos"
            assert data["apellido"] == "García"
        finally:
            await client.aclose()

        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await eng.dispose()

    async def test_update_perfil_with_cuil_returns_422(self):
        await close_db_engine()
        eng = create_async_engine(DB_URL, echo=False)
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        factory = async_sessionmaker(eng, expire_on_commit=False)

        async with factory() as session:
            tenant = Tenant(id=TENANT_ID, name="Test", slug="test-tenant", code="TEST")
            session.add(tenant)
            user = Usuario(
                id=uuid.uuid4(),
                tenant_id=TENANT_ID,
                email="user@test.com",
                hashed_password=hash_password("testpass123"),
                nombre="Juan",
                is_active=True,
            )
            session.add(user)
            await session.commit()
            user_id = user.id

        token = create_access_token({"sub": str(user_id), "tenant_id": str(TENANT_ID), "roles": []})
        headers = {"Authorization": f"Bearer {token}"}

        client = await _make_client()
        try:
            resp = await client.patch(
                "/api/perfil",
                json={"cuil": "20-12345678-9"},
                headers=headers,
            )
            assert resp.status_code == 422, resp.text
        finally:
            await client.aclose()

        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await eng.dispose()
