"""Integration tests for user-role assignment endpoints and permission resolution."""
import os

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import close_db_engine
from tests.db_utils import drop_enum_types
from app.core.security import create_access_token, hash_password
from app.models.role import Role
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.models.usuario_role import UsuarioRole

pytestmark = pytest.mark.asyncio

_db_host = os.environ.get('POSTGRES_HOST', 'localhost')
DB_URL = f"postgresql+asyncpg://active_trace:active_trace@{_db_host}:5432/active_trace_test"
TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
TENANT2_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


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


async def _seed_tenant(eng, tenant_id=TENANT_ID, slug="test-tenant", code="TEST"):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        tenant = Tenant(id=tenant_id, name="Test", slug=slug, code=code)
        session.add(tenant)
        await session.commit()


async def _seed_user(eng, tenant_id=TENANT_ID, email="admin@test.com"):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        user = Usuario(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            email=email,
            hashed_password=hash_password("testpass123"),
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
            permissions=permissions or ["roles:gestionar"],
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


async def _setup_admin_user(eng):
    await _seed_tenant(eng)
    user = await _seed_user(eng)
    admin_role = await _seed_role(eng)
    await _assign_role(eng, user.id, admin_role.id)
    token = create_access_token({"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]})
    return user, token


class TestUserRoleAssignment:
    async def test_assign_role_to_user(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            admin_user, admin_token = await _setup_admin_user(eng)
            target_user = await _seed_user(eng, email="target@test.com")
            role = await _seed_role(eng, name="PROFESOR", permissions=["calificaciones:importar"], system=True)

            async with await _make_app() as client:
                response = await client.post(
                    f"/api/users/{target_user.id}/roles",
                    json={"role_id": str(role.id)},
                    headers={"Authorization": f"Bearer {admin_token}"},
                )
            assert response.status_code == 201
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_get_user_roles(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            admin_user, admin_token = await _setup_admin_user(eng)
            target_user = await _seed_user(eng, email="target2@test.com")
            role = await _seed_role(eng, name="TUTOR", permissions=["atrasados:ver"], system=True)
            await _assign_role(eng, target_user.id, role.id)

            async with await _make_app() as client:
                response = await client.get(
                    f"/api/users/{target_user.id}/roles",
                    headers={"Authorization": f"Bearer {admin_token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert any(r["name"] == "TUTOR" for r in data)
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_remove_role_from_user(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            admin_user, admin_token = await _setup_admin_user(eng)
            target_user = await _seed_user(eng, email="target3@test.com")
            role = await _seed_role(eng, name="REMOVABLE", permissions=["test:x"], system=False)
            await _assign_role(eng, target_user.id, role.id)

            async with await _make_app() as client:
                response = await client.delete(
                    f"/api/users/{target_user.id}/roles/{role.id}",
                    headers={"Authorization": f"Bearer {admin_token}"},
                )
            assert response.status_code == 204
        finally:
            await _teardown_db()
            await eng.dispose()


class TestPermissionResolution:
    async def test_current_user_has_permissions_from_single_role(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng, name="VIEWER", permissions=["usuarios:list"], system=False)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token({"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["VIEWER"]})

            async with await _make_app() as client:
                response = await client.get(
                    "/api/roles",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403

            role2 = await _seed_role(eng, name="ADMIN2", permissions=["roles:gestionar", "usuarios:list"], system=False)
            await _assign_role(eng, user.id, role2.id)
            token2 = create_access_token({"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN2"]})

            async with await _make_app() as client:
                response = await client.get(
                    "/api/roles",
                    headers={"Authorization": f"Bearer {token2}"},
                )
            assert response.status_code == 200
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_permissions_union_across_multiple_roles(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role_a = await _seed_role(eng, name="ROLE_A", permissions=["usuarios:list"], system=False)
            role_b = await _seed_role(eng, name="ROLE_B", permissions=["roles:gestionar"], system=False)
            await _assign_role(eng, user.id, role_a.id)
            await _assign_role(eng, user.id, role_b.id)
            token = create_access_token({"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ROLE_A", "ROLE_B"]})

            async with await _make_app() as client:
                response = await client.get(
                    "/api/roles",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
        finally:
            await _teardown_db()
            await eng.dispose()
