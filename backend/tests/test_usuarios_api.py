"""Integration tests for usuarios and asignaciones endpoints."""
import os

import uuid
from datetime import date

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base, close_db_engine
from app.core.security import create_access_token, encrypt_value, hash_password
from tests.db_utils import drop_enum_types
from app.models.asignacion import Asignacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
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
    eng = create_async_engine(DB_URL, echo=False)
    async with eng.begin() as conn:
        await drop_enum_types(conn)
        await conn.run_sync(Base.metadata.create_all)
    await eng.dispose()


async def _teardown_db():
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


async def _seed_user(
    eng, tenant_id=TENANT_ID, email="admin@test.com", password="testpass123",
    nombre="Admin", apellido="User",
):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        user = Usuario(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            email=email,
            hashed_password=hash_password(password),
            is_active=True,
            nombre=nombre,
            apellido=apellido,
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
            permissions=permissions
            or ["estructura:gestionar", "roles:gestionar", "usuarios:gestionar", "usuarios:asignar"],
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


class TestUsuarioRead:
    async def test_list_usuarios_returns_safe_schema(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng, email="user1@test.com")
            await _seed_user(eng, email="user2@test.com")
            admin_role = await _seed_role(eng, permissions=["usuarios:gestionar"])
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                response = await client.get(
                    "/api/admin/usuarios",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 2
            assert len(data["items"]) == 2
            assert "dni" not in data["items"][0]
            assert "cuil" not in data["items"][0]
            assert "cbu" not in data["items"][0]
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_list_usuarios_filters_by_nombre(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng, email="admin@test.com", nombre="Carlos")
            await _seed_user(eng, email="other@test.com", nombre="Maria")
            admin_role = await _seed_role(eng, permissions=["usuarios:gestionar"])
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                response = await client.get(
                    "/api/admin/usuarios?nombre=Carlos",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["total"] == 1
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_list_usuarios_filters_by_is_active(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                inactive = Usuario(
                    id=uuid.uuid4(), tenant_id=TENANT_ID, email="inactive@test.com",
                    hashed_password=hash_password("p"), is_active=False,
                    nombre="Inactive", apellido="User",
                )
                session.add(inactive)
                await session.commit()
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["usuarios:gestionar"])
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                response = await client.get(
                    "/api/admin/usuarios?is_active=false",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["total"] == 1
        finally:
            await _teardown_db()
            await eng.dispose()


class TestUsuarioDetail:
    async def test_get_usuario_without_ver_pii_hides_pii(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["usuarios:gestionar"])
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                response = await client.get(
                    f"/api/admin/usuarios/{user.id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert data["dni"] is None
            assert data["cuil"] is None
            assert data["cbu"] is None
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_get_usuario_with_ver_pii_shows_decrypted_pii(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                user = Usuario(
                    id=uuid.uuid4(), tenant_id=TENANT_ID, email="pii@test.com",
                    hashed_password=hash_password("p"), is_active=True,
                    nombre="PII", apellido="User",
                    dni=encrypt_value("12345678"),
                    cuil=encrypt_value("20-12345678-9"),
                    cbu=encrypt_value("00000031000123456789"),
                )
                session.add(user)
                await session.commit()

            admin_role = await _seed_role(
                eng, permissions=["usuarios:gestionar", "usuarios:ver-pii"],
            )
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                response = await client.get(
                    f"/api/admin/usuarios/{user.id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert data["dni"] == "12345678"
            assert data["cuil"] == "20-12345678-9"
            assert data["cbu"] == "00000031000123456789"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_get_usuario_not_found(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["usuarios:gestionar"])
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                response = await client.get(
                    f"/api/admin/usuarios/{uuid.uuid4()}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 404
        finally:
            await _teardown_db()
            await eng.dispose()


class TestUsuarioUpdate:
    async def test_partial_update_usuario(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["usuarios:gestionar"])
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                response = await client.put(
                    f"/api/admin/usuarios/{user.id}",
                    json={"nombre": "UpdatedName", "telefono": "123456789"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert data["nombre"] == "UpdatedName"
            assert data["telefono"] == "123456789"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_update_legajo_unique_per_tenant(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                user_a = Usuario(
                    id=uuid.uuid4(), tenant_id=TENANT_ID, email="a@test.com",
                    hashed_password=hash_password("p"), is_active=True,
                    nombre="A", apellido="User", legajo="L-001",
                )
                user_b = Usuario(
                    id=uuid.uuid4(), tenant_id=TENANT_ID, email="b@test.com",
                    hashed_password=hash_password("p"), is_active=True,
                    nombre="B", apellido="User",
                )
                session.add_all([user_a, user_b])
                await session.commit()

            admin_role = await _seed_role(eng, permissions=["usuarios:gestionar"])
            await _assign_role(eng, user_a.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user_a.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                response = await client.put(
                    f"/api/admin/usuarios/{user_b.id}",
                    json={"legajo": "L-001"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 409
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_same_legajo_allowed_across_tenants(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng, TENANT_ID, "tenant-a", "TEN_A")
            await _seed_tenant(eng, TENANT2_ID, "tenant-b", "TEN_B")

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                user_a = Usuario(
                    id=uuid.uuid4(), tenant_id=TENANT_ID, email="a@a.com",
                    hashed_password=hash_password("p"), is_active=True,
                    nombre="A", apellido="User", legajo="L-001",
                )
                user_b = Usuario(
                    id=uuid.uuid4(), tenant_id=TENANT2_ID, email="b@b.com",
                    hashed_password=hash_password("p"), is_active=True,
                    nombre="B", apellido="User",
                )
                session.add_all([user_a, user_b])
                await session.commit()

            admin_role_a = await _seed_role(
                eng, TENANT_ID, "ADMIN_A", ["usuarios:gestionar"],
            )
            admin_role_b = await _seed_role(
                eng, TENANT2_ID, "ADMIN_B", ["usuarios:gestionar"],
            )
            await _assign_role(eng, user_a.id, admin_role_a.id, TENANT_ID)
            await _assign_role(eng, user_b.id, admin_role_b.id, TENANT2_ID)
            token_b = create_access_token(
                {"sub": str(user_b.id), "tenant_id": str(TENANT2_ID), "roles": ["ADMIN_B"]},
            )

            async with await _make_app() as client:
                response = await client.put(
                    f"/api/admin/usuarios/{user_b.id}",
                    json={"legajo": "L-001"},
                    headers={"Authorization": f"Bearer {token_b}"},
                )
            assert response.status_code == 200
            assert response.json()["legajo"] == "L-001"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_update_pii_fields_nullable(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["usuarios:gestionar", "usuarios:ver-pii"])
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                response = await client.put(
                    f"/api/admin/usuarios/{user.id}",
                    json={"dni": "87654321", "cuil": "20-87654321-0", "cbu": "00000031000123456789"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert data["dni"] == "87654321"
            assert data["cuil"] == "20-87654321-0"
            assert data["cbu"] == "00000031000123456789"
        finally:
            await _teardown_db()
            await eng.dispose()


class TestMultiTenantUsuario:
    async def test_multi_tenant_isolation(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng, TENANT_ID, "tenant-a", "TEN_A")
            await _seed_tenant(eng, TENANT2_ID, "tenant-b", "TEN_B")

            user_a = await _seed_user(eng, TENANT_ID, "a@a.com")
            await _seed_user(eng, TENANT2_ID, "b@b.com")
            admin_a = await _seed_role(eng, TENANT_ID, "ADMIN_A", ["usuarios:gestionar"])
            await _assign_role(eng, user_a.id, admin_a.id, TENANT_ID)
            token_a = create_access_token(
                {"sub": str(user_a.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN_A"]},
            )

            async with await _make_app() as client:
                response = await client.get(
                    "/api/admin/usuarios",
                    headers={"Authorization": f"Bearer {token_a}"},
                )
            assert response.status_code == 200
            assert response.json()["total"] == 1
        finally:
            await _teardown_db()
            await eng.dispose()


class TestAsignacionCrud:
    async def test_create_asignacion(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["usuarios:gestionar", "usuarios:asignar"])
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                response = await client.post(
                    "/api/admin/asignaciones",
                    json={"usuario_id": str(user.id), "rol": "PROFESOR"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 201
            data = response.json()
            assert data["rol"] == "PROFESOR"
            assert data["usuario_id"] == str(user.id)
            assert data["is_active"] is True
            assert "id" in data
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_get_asignacion(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["usuarios:gestionar", "usuarios:asignar"])
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                created = await client.post(
                    "/api/admin/asignaciones",
                    json={"usuario_id": str(user.id), "rol": "TUTOR"},
                    headers={"Authorization": f"Bearer {token}"},
                )
                asignacion_id = created.json()["id"]
                response = await client.get(
                    f"/api/admin/asignaciones/{asignacion_id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["rol"] == "TUTOR"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_update_asignacion(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["usuarios:gestionar", "usuarios:asignar"])
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                created = await client.post(
                    "/api/admin/asignaciones",
                    json={"usuario_id": str(user.id), "rol": "TUTOR"},
                    headers={"Authorization": f"Bearer {token}"},
                )
                asignacion_id = created.json()["id"]
                response = await client.put(
                    f"/api/admin/asignaciones/{asignacion_id}",
                    json={"rol": "PROFESOR"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["rol"] == "PROFESOR"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_soft_delete_asignacion(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["usuarios:gestionar", "usuarios:asignar"])
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                created = await client.post(
                    "/api/admin/asignaciones",
                    json={"usuario_id": str(user.id), "rol": "TUTOR"},
                    headers={"Authorization": f"Bearer {token}"},
                )
                asignacion_id = created.json()["id"]
                response = await client.delete(
                    f"/api/admin/asignaciones/{asignacion_id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
                get_resp = await client.get(
                    f"/api/admin/asignaciones/{asignacion_id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 204
            assert get_resp.status_code == 404
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_list_asignaciones(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["usuarios:gestionar", "usuarios:asignar"])
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                await client.post(
                    "/api/admin/asignaciones",
                    json={"usuario_id": str(user.id), "rol": "PROFESOR"},
                    headers={"Authorization": f"Bearer {token}"},
                )
                await client.post(
                    "/api/admin/asignaciones",
                    json={"usuario_id": str(user.id), "rol": "TUTOR"},
                    headers={"Authorization": f"Bearer {token}"},
                )
                response = await client.get(
                    "/api/admin/asignaciones",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["total"] == 2
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_asignacion_not_found(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["usuarios:gestionar", "usuarios:asignar"])
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                response = await client.get(
                    f"/api/admin/asignaciones/{uuid.uuid4()}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 404
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_create_asignacion_nonexistent_usuario_rejected(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["usuarios:gestionar", "usuarios:asignar"])
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                response = await client.post(
                    "/api/admin/asignaciones",
                    json={"usuario_id": str(uuid.uuid4()), "rol": "PROFESOR"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 400
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_create_asignacion_default_fecha_inicio(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["usuarios:gestionar", "usuarios:asignar"])
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                response = await client.post(
                    "/api/admin/asignaciones",
                    json={"usuario_id": str(user.id), "rol": "PROFESOR"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 201
            data = response.json()
            assert data["fecha_inicio"] == date.today().isoformat()
        finally:
            await _teardown_db()
            await eng.dispose()


class TestUsuarioAsignaciones:
    async def test_get_assignments_for_usuario(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["usuarios:gestionar", "usuarios:asignar"])
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                await client.post(
                    "/api/admin/asignaciones",
                    json={"usuario_id": str(user.id), "rol": "PROFESOR"},
                    headers={"Authorization": f"Bearer {token}"},
                )
                response = await client.get(
                    f"/api/admin/usuarios/{user.id}/asignaciones",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["total"] == 1
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_get_assignments_for_nonexistent_usuario_returns_404(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["usuarios:gestionar", "usuarios:asignar"])
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                response = await client.get(
                    f"/api/admin/usuarios/{uuid.uuid4()}/asignaciones",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 404
        finally:
            await _teardown_db()
            await eng.dispose()


class TestPermissionGuard:
    async def test_usuarios_gestionar_required(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            no_perm_role = await _seed_role(
                eng, name="LIMITED", permissions=["test:read"], system=False,
            )
            await _assign_role(eng, user.id, no_perm_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["LIMITED"]},
            )

            async with await _make_app() as client:
                response = await client.get(
                    "/api/admin/usuarios",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_usuarios_asignar_required_for_asignaciones(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            no_perm_role = await _seed_role(
                eng, name="LIMITED", permissions=["test:read"], system=False,
            )
            await _assign_role(eng, user.id, no_perm_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["LIMITED"]},
            )

            async with await _make_app() as client:
                response = await client.post(
                    "/api/admin/asignaciones",
                    json={"usuario_id": str(user.id), "rol": "PROFESOR"},
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
                    "/api/admin/asignaciones",
                    json={"usuario_id": str(uuid.uuid4()), "rol": "PROFESOR"},
                )
            assert response.status_code == 401
        finally:
            await _teardown_db()
            await eng.dispose()
