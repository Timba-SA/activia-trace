"""Integration tests for role CRUD endpoints and require_permission guard."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import close_db_engine
from app.core.security import create_access_token, hash_password
from app.models.role import Role
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.models.usuario_role import UsuarioRole

pytestmark = pytest.mark.asyncio

DB_URL = "postgresql+asyncpg://active_trace:active_trace@localhost:5432/active_trace_test"
TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
TENANT2_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


async def _setup_db():
    from app.core.database import Base
    eng = create_async_engine(DB_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await eng.dispose()


async def _teardown_db():
    from app.core.database import Base
    eng = create_async_engine(DB_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()
    await close_db_engine()


async def _seed_tenant(eng, tenant_id=TENANT_ID, slug="test-tenant", code="TEST"):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        tenant = Tenant(id=tenant_id, name="Test", slug=slug, code=code)
        session.add(tenant)
        await session.commit()


async def _seed_user(eng, tenant_id=TENANT_ID, email="admin@test.com", password="testpass123"):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        user = Usuario(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            email=email,
            hashed_password=hash_password(password),
            is_active=True,
        )
        session.add(user)
        await session.commit()
        return user


async def _seed_role(eng, tenant_id=TENANT_ID, name="ADMIN", permissions=None, system=True):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        role = Role(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name=name,
            permissions=permissions or ["roles:gestionar", "usuarios:gestionar"],
            is_system_role=system,
        )
        session.add(role)
        await session.commit()
        return role


async def _assign_role(eng, user_id, role_id, tenant_id=TENANT_ID):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        session.add(UsuarioRole(usuario_id=user_id, role_id=role_id, tenant_id=tenant_id))
        await session.commit()


async def _make_app():
    from app.main import create_app
    app = create_app()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


class TestRoleCrud:
    async def test_create_role(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)

            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token({"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]})

            async with await _make_app() as client:
                response = await client.post(
                    "/api/roles",
                    json={"name": "NewRole", "permissions": ["test:action"]},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == "NewRole"
            assert data["permissions"] == ["test:action"]
            assert data["is_system_role"] is False
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_create_role_duplicate_name(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, name="TestRole")
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token({"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]})

            async with await _make_app() as client:
                await client.post(
                    "/api/roles",
                    json={"name": "TestRole", "permissions": []},
                    headers={"Authorization": f"Bearer {token}"},
                )
                response = await client.post(
                    "/api/roles",
                    json={"name": "TestRole", "permissions": []},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 409
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_list_roles(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _seed_role(eng, name="USER", permissions=["test:read"], system=False)
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token({"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]})

            async with await _make_app() as client:
                response = await client.get(
                    "/api/roles",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert data["total"] >= 2
            assert len(data["items"]) >= 2
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_get_role_by_id(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token({"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]})

            async with await _make_app() as client:
                response = await client.get(
                    f"/api/roles/{admin_role.id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["name"] == "ADMIN"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_update_role_permissions(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token({"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]})

            async with await _make_app() as client:
                response = await client.put(
                    f"/api/roles/{admin_role.id}",
                    json={"permissions": ["new:perm1", "new:perm2"]},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["permissions"] == ["new:perm1", "new:perm2"]
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_delete_non_system_role(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            custom_role = await _seed_role(eng, name="CUSTOM", permissions=["test:x"], system=False)
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token({"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]})

            async with await _make_app() as client:
                response = await client.delete(
                    f"/api/roles/{custom_role.id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 204
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_delete_system_role_forbidden(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token({"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]})

            async with await _make_app() as client:
                response = await client.delete(
                    f"/api/roles/{admin_role.id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()


class TestRequirePermission:
    async def test_authorized_passes(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token({"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]})

            async with await _make_app() as client:
                response = await client.get(
                    "/api/roles",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_unauthorized_returns_403(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            no_perm_role = await _seed_role(eng, name="LIMITED", permissions=["test:read"], system=False)
            await _assign_role(eng, user.id, no_perm_role.id)
            token = create_access_token({"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["LIMITED"]})

            async with await _make_app() as client:
                response = await client.get(
                    "/api/roles",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_unauthenticated_rejected(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)

            async with await _make_app() as client:
                response = await client.post(
                    "/api/roles",
                    json={"name": "X", "permissions": []},
                )
            assert response.status_code == 401
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_user_without_roles_gets_403(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            token = create_access_token({"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": []})

            async with await _make_app() as client:
                response = await client.get(
                    "/api/roles",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()
