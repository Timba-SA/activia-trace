"""Integration tests for padron CRUD and upload endpoints."""
import os
import pytest_asyncio
import os

import io
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base, close_db_engine
from app.core.security import create_access_token, hash_password
from tests.db_utils import drop_enum_types
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
        existing = await session.get(Tenant, tenant_id)
        if existing is None:
            tenant = Tenant(id=tenant_id, name="Test", slug=slug, code=code)
            session.add(tenant)
            await session.commit()


async def _seed_user(eng, tenant_id=TENANT_ID, email="admin@test.com", password="testpass123"):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        user = Usuario(
            id=uuid.uuid4(),
            email=email,
            tenant_id=tenant_id,
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
            permissions=permissions or ["padron:cargar", "estructura:gestionar"],
            is_system_role=system,
        )
        session.add(role)
        await session.commit()
        return role


async def _seed_role_no_permission(eng, tenant_id=TENANT_ID, name="VIEWER"):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        role = Role(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name=name,
            permissions=["academico:ver_estado_propio"],
            is_system_role=True,
        )
        session.add(role)
        await session.commit()
        return role


async def _assign_role(eng, user_id, role_id, tenant_id=TENANT_ID):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        session.add(UsuarioRole(usuario_id=user_id, role_id=role_id, tenant_id=tenant_id))
        await session.commit()


async def _seed_carrera(eng, tenant_id=TENANT_ID):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        carrera = Carrera(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            codigo=f"TUPAD-{uuid.uuid4().hex[:6]}",
            nombre="Tecnicatura",
            is_active=True,
        )
        session.add(carrera)
        await session.commit()
        return carrera


async def _seed_cohorte(eng, tenant_id=TENANT_ID, carrera_id=None):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        cohorte = Cohorte(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            carrera_id=carrera_id,
            nombre=f"MAR-{uuid.uuid4().hex[:6]}",
            anio=2026,
            is_active=True,
        )
        session.add(cohorte)
        await session.commit()
        return cohorte


async def _seed_materia(eng, tenant_id=TENANT_ID):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        materia = Materia(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            codigo=f"MAT-{uuid.uuid4().hex[:6]}",
            nombre="Materia Test",
            is_active=True,
        )
        session.add(materia)
        await session.commit()
        return materia


async def _create_auth_headers(eng, user=None, tenant_id=TENANT_ID):
    if user is None:
        user = await _seed_user(eng, tenant_id)
    token = create_access_token({"sub": str(user.id), "tenant_id": str(tenant_id), "roles": ["ADMIN"]})
    return {"Authorization": f"Bearer {token}"}


async def _build_test_data(eng, tenant_id=TENANT_ID, slug="test-tenant", code="TEST"):
    await _seed_tenant(eng, tenant_id, slug, code)
    carrera = await _seed_carrera(eng, tenant_id)
    cohorte = await _seed_cohorte(eng, tenant_id, carrera.id)
    materia = await _seed_materia(eng, tenant_id)
    user = await _seed_user(eng, tenant_id)
    role = await _seed_role(eng, tenant_id)
    await _assign_role(eng, user.id, role.id, tenant_id)
    return user, materia, cohorte, carrera


@pytest_asyncio.fixture(autouse=True)
async def setup_teardown():
    await _setup_db()
    yield
    await _teardown_db()


@pytest_asyncio.fixture
async def client():
    from app.main import create_app
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
    await close_db_engine()


@pytest_asyncio.fixture
async def eng():
    engine = create_async_engine(DB_URL, echo=False)
    yield engine
    await engine.dispose()


class TestUploadFlow:
    async def test_preview_upload_creates_preview(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)

        content = "legajo,nombre_completo,email,estado\n1234,Juan Perez,juan@test.com,activo\n5678,Ana Gomez,ana@test.com,activo"
        files = {"file": ("alumnos.csv", io.BytesIO(content.encode("utf-8")), "text/csv")}
        resp = await client.post(
            f"/api/v1/padron/upload?materia_id={materia.id}&cohorte_id={cohorte.id}",
            files=files,
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_rows"] == 2
        assert len(data["entries"]) == 2
        assert data["entries"][0]["legajo"] == "1234"
        assert data["preview_hash"] is not None

    async def test_confirm_upload_creates_version_and_entradas(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)

        content = "legajo,nombre_completo,email,estado\n1111,User One,user1@test.com,activo"
        files = {"file": ("alumnos.csv", io.BytesIO(content.encode("utf-8")), "text/csv")}
        preview_resp = await client.post(
            f"/api/v1/padron/upload?materia_id={materia.id}&cohorte_id={cohorte.id}",
            files=files,
            headers=headers,
        )
        assert preview_resp.status_code == 200
        preview = preview_resp.json()

        confirm_resp = await client.post(
            "/api/v1/padron/confirm",
            json={
                "materia_id": str(materia.id),
                "cohorte_id": str(cohorte.id),
                "preview_hash": preview["preview_hash"],
                "entries": preview["entries"],
            },
            headers=headers,
        )
        if confirm_resp.status_code != 201:
            print(f"CONFIRM ERROR: {confirm_resp.status_code} {confirm_resp.text}")
        assert confirm_resp.status_code == 201
        data = confirm_resp.json()
        assert data["total_entradas"] == 1
        assert data["activa"] is True


class TestVersioning:
    async def test_second_upload_deactivates_previous_version(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)

        content1 = "legajo,nombre_completo,email,estado\n1111,User One,user1@test.com,activo"
        files1 = {"file": ("a.csv", io.BytesIO(content1.encode("utf-8")), "text/csv")}
        preview1 = await client.post(
            f"/api/v1/padron/upload?materia_id={materia.id}&cohorte_id={cohorte.id}",
            files=files1, headers=headers,
        )
        assert preview1.status_code == 200
        p1 = preview1.json()
        confirm1 = await client.post(
            "/api/v1/padron/confirm",
            json={
                "materia_id": str(materia.id),
                "cohorte_id": str(cohorte.id),
                "preview_hash": p1["preview_hash"],
                "entries": p1["entries"],
            },
            headers=headers,
        )
        if confirm1.status_code != 201:
            print(f"CONFIRM1 ERROR: {confirm1.status_code} {confirm1.text}")
        assert confirm1.status_code == 201
        version1_id = confirm1.json()["version_id"]

        content2 = "legajo,nombre_completo,email,estado\n2222,User Two,user2@test.com,activo"
        files2 = {"file": ("b.csv", io.BytesIO(content2.encode("utf-8")), "text/csv")}
        preview2 = await client.post(
            f"/api/v1/padron/upload?materia_id={materia.id}&cohorte_id={cohorte.id}",
            files=files2, headers=headers,
        )
        assert preview2.status_code == 200
        p2 = preview2.json()
        confirm2 = await client.post(
            "/api/v1/padron/confirm",
            json={
                "materia_id": str(materia.id),
                "cohorte_id": str(cohorte.id),
                "preview_hash": p2["preview_hash"],
                "entries": p2["entries"],
            },
            headers=headers,
        )
        if confirm2.status_code != 201:
            print(f"CONFIRM2 ERROR: {confirm2.status_code} {confirm2.text}")
        assert confirm2.status_code == 201
        version2_id = confirm2.json()["version_id"]
        assert version1_id != version2_id

        active_resp = await client.get(
            f"/api/v1/padron/activo?materia_id={materia.id}&cohorte_id={cohorte.id}",
            headers=headers,
        )
        assert active_resp.status_code == 200
        active_data = active_resp.json()
        assert active_data["id"] == version2_id
        assert active_data["activa"] is True


class TestTenantIsolation:
    async def test_tenant_a_cannot_see_tenant_b_versions(self, client, eng):
        user_a, materia_a, cohorte_a, _ = await _build_test_data(eng, TENANT_ID, "test-tenant", "TEST")
        user_b, materia_b, cohorte_b, _ = await _build_test_data(eng, TENANT2_ID, "tenant-2", "T2")

        headers_b = await _create_auth_headers(eng, user_b, TENANT2_ID)

        content = "legajo,nombre_completo,email,estado\n9999,Tenant B User,tb@test.com,activo"
        files = {"file": ("c.csv", io.BytesIO(content.encode("utf-8")), "text/csv")}
        preview = await client.post(
            f"/api/v1/padron/upload?materia_id={materia_b.id}&cohorte_id={cohorte_b.id}",
            files=files, headers=headers_b,
        )
        assert preview.status_code == 200
        p = preview.json()
        confirm = await client.post(
            "/api/v1/padron/confirm",
            json={
                "materia_id": str(materia_b.id),
                "cohorte_id": str(cohorte_b.id),
                "preview_hash": p["preview_hash"],
                "entries": p["entries"],
            },
            headers=headers_b,
        )
        if confirm.status_code != 201:
            print(f"TENANT CONFIRM ERROR: {confirm.status_code} {confirm.text}")
        assert confirm.status_code == 201

        headers_a = await _create_auth_headers(eng, user_a, TENANT_ID)
        resp_a = await client.get(
            f"/api/v1/padron/versiones?materia_id={materia_b.id}&cohorte_id={cohorte_b.id}",
            headers=headers_a,
        )
        assert resp_a.status_code == 200
        data_a = resp_a.json()
        assert data_a["total"] == 0


class TestPermissionGuard:
    async def test_upload_without_permission_returns_403(self, client, eng):
        await _seed_tenant(eng)
        user = await _seed_user(eng)
        await _seed_role_no_permission(eng)
        headers = await _create_auth_headers(eng, user)

        content = "legajo,nombre_completo,email,estado\n0000,Nobody,no@test.com,activo"
        files = {"file": ("d.csv", io.BytesIO(content.encode("utf-8")), "text/csv")}
        resp = await client.post(
            f"/api/v1/padron/upload?materia_id={uuid.uuid4()}&cohorte_id={uuid.uuid4()}",
            files=files, headers=headers,
        )
        assert resp.status_code == 403


class TestEntradaSinUsuario:
    async def test_entrada_sin_usuario_id(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)

        content = "legajo,nombre_completo,email,estado\n7777,No Account,noaccount@test.com,activo"
        files = {"file": ("e.csv", io.BytesIO(content.encode("utf-8")), "text/csv")}
        preview = await client.post(
            f"/api/v1/padron/upload?materia_id={materia.id}&cohorte_id={cohorte.id}",
            files=files, headers=headers,
        )
        assert preview.status_code == 200
        p = preview.json()
        confirm = await client.post(
            "/api/v1/padron/confirm",
            json={
                "materia_id": str(materia.id),
                "cohorte_id": str(cohorte.id),
                "preview_hash": p["preview_hash"],
                "entries": p["entries"],
            },
            headers=headers,
        )
        if confirm.status_code != 201:
            print(f"ENTRADA CONFIRM ERROR: {confirm.status_code} {confirm.text}")
        assert confirm.status_code == 201

        version_id = confirm.json()["version_id"]
        entries_resp = await client.get(
            f"/api/v1/padron/versiones/{version_id}/entradas",
            headers=headers,
        )
        entries = entries_resp.json()
        assert entries["total"] == 1
        assert entries["items"][0]["usuario_id"] is None
