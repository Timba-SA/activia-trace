"""Integration tests for estructura-academica CRUD endpoints."""
import os

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
        tenant = Tenant(id=tenant_id, name="Test", slug=slug, code=code)
        session.add(tenant)
        await session.commit()


async def _seed_user(
    eng, tenant_id=TENANT_ID, email="admin@test.com", password="testpass123",
):
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
            permissions=permissions
            or ["estructura:gestionar", "roles:gestionar", "usuarios:gestionar"],
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


class TestCarreraCrud:
    async def test_create_carrera(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                response = await client.post(
                    "/api/admin/carreras",
                    json={"codigo": "ING-2026", "nombre": "Ingeniería 2026", "duracion_anios": 5},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 201
            data = response.json()
            assert data["codigo"] == "ING-2026"
            assert data["nombre"] == "Ingeniería 2026"
            assert data["duracion_anios"] == 5
            assert data["is_active"] is True
            assert "id" in data
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_create_carrera_duplicate_codigo(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                await client.post(
                    "/api/admin/carreras",
                    json={"codigo": "ING-2026", "nombre": "Ingeniería"},
                    headers={"Authorization": f"Bearer {token}"},
                )
                response = await client.post(
                    "/api/admin/carreras",
                    json={"codigo": "ING-2026", "nombre": "Duplicado"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 409
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_multi_tenant_isolation(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng, TENANT_ID, "tenant-a", "TEN_A")
            await _seed_tenant(eng, TENANT2_ID, "tenant-b", "TEN_B")

            user_a = await _seed_user(eng, TENANT_ID, "admin@a.com")
            user_b = await _seed_user(eng, TENANT2_ID, "admin@b.com")
            admin_a = await _seed_role(eng, TENANT_ID, "ADMIN_A", ["estructura:gestionar"])
            admin_b = await _seed_role(eng, TENANT2_ID, "ADMIN_B", ["estructura:gestionar"])
            await _assign_role(eng, user_a.id, admin_a.id, TENANT_ID)
            await _assign_role(eng, user_b.id, admin_b.id, TENANT2_ID)

            token_a = create_access_token(
                {"sub": str(user_a.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN_A"]},
            )
            token_b = create_access_token(
                {"sub": str(user_b.id), "tenant_id": str(TENANT2_ID), "roles": ["ADMIN_B"]},
            )

            async with await _make_app() as client:
                resp_a = await client.post(
                    "/api/admin/carreras",
                    json={"codigo": "ING", "nombre": "Ingeniería"},
                    headers={"Authorization": f"Bearer {token_a}"},
                )
                assert resp_a.status_code == 201

                resp_b = await client.post(
                    "/api/admin/carreras",
                    json={"codigo": "ING", "nombre": "Ingeniería B"},
                    headers={"Authorization": f"Bearer {token_b}"},
                )
                assert resp_b.status_code == 201

                list_a = await client.get(
                    "/api/admin/carreras",
                    headers={"Authorization": f"Bearer {token_a}"},
                )
            assert list_a.status_code == 200
            assert list_a.json()["total"] == 1
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_list_carreras(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                await client.post(
                    "/api/admin/carreras",
                    json={"codigo": "C1", "nombre": "Carrera 1"},
                    headers={"Authorization": f"Bearer {token}"},
                )
                await client.post(
                    "/api/admin/carreras",
                    json={"codigo": "C2", "nombre": "Carrera 2"},
                    headers={"Authorization": f"Bearer {token}"},
                )
                response = await client.get(
                    "/api/admin/carreras",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 2
            assert len(data["items"]) == 2
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_get_carrera_by_id(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                created = await client.post(
                    "/api/admin/carreras",
                    json={"codigo": "C1", "nombre": "Mi Carrera"},
                    headers={"Authorization": f"Bearer {token}"},
                )
                carrera_id = created.json()["id"]
                response = await client.get(
                    f"/api/admin/carreras/{carrera_id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["nombre"] == "Mi Carrera"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_get_carrera_not_found(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                response = await client.get(
                    f"/api/admin/carreras/{uuid.uuid4()}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 404
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_update_carrera(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                created = await client.post(
                    "/api/admin/carreras",
                    json={"codigo": "C1", "nombre": "Original"},
                    headers={"Authorization": f"Bearer {token}"},
                )
                carrera_id = created.json()["id"]
                response = await client.put(
                    f"/api/admin/carreras/{carrera_id}",
                    json={"nombre": "Updated"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["nombre"] == "Updated"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_soft_delete_carrera(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                created = await client.post(
                    "/api/admin/carreras",
                    json={"codigo": "C1", "nombre": "To Delete"},
                    headers={"Authorization": f"Bearer {token}"},
                )
                carrera_id = created.json()["id"]
                response = await client.delete(
                    f"/api/admin/carreras/{carrera_id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
                get_resp = await client.get(
                    f"/api/admin/carreras/{carrera_id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 204
            assert get_resp.status_code == 404
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_delete_carrera_with_cohortes_rejected(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                carrera_resp = await client.post(
                    "/api/admin/carreras",
                    json={"codigo": "C1", "nombre": "Carrera"},
                    headers={"Authorization": f"Bearer {token}"},
                )
                carrera_id = carrera_resp.json()["id"]

                await client.post(
                    "/api/admin/cohortes",
                    json={"carrera_id": carrera_id, "nombre": "2026", "anio": 2026},
                    headers={"Authorization": f"Bearer {token}"},
                )

                response = await client.delete(
                    f"/api/admin/carreras/{carrera_id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 409
        finally:
            await _teardown_db()
            await eng.dispose()


class TestCohorteCrud:
    async def _seed_carrera(self, eng, tenant_id=TENANT_ID):
        factory = async_sessionmaker(eng, expire_on_commit=False)
        async with factory() as session:
            carrera = Carrera(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                codigo="CARR-001",
                nombre="Test Carrera",
                is_active=True,
            )
            session.add(carrera)
            await session.commit()
            return carrera

    async def test_create_cohorte(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            carrera = await self._seed_carrera(eng)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                response = await client.post(
                    "/api/admin/cohortes",
                    json={
                        "carrera_id": str(carrera.id),
                        "nombre": "2026-A",
                        "anio": 2026,
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 201
            data = response.json()
            assert data["nombre"] == "2026-A"
            assert data["anio"] == 2026
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_create_cohorte_duplicate_nombre(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            carrera = await self._seed_carrera(eng)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                await client.post(
                    "/api/admin/cohortes",
                    json={
                        "carrera_id": str(carrera.id),
                        "nombre": "2026-A",
                        "anio": 2026,
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
                response = await client.post(
                    "/api/admin/cohortes",
                    json={
                        "carrera_id": str(carrera.id),
                        "nombre": "2026-A",
                        "anio": 2026,
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 409
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_create_cohorte_inactive_carrera_rejected(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                carrera = Carrera(
                    id=uuid.uuid4(),
                    tenant_id=TENANT_ID,
                    codigo="CARR-INACTIVE",
                    nombre="Inactive Carrera",
                    is_active=False,
                )
                session.add(carrera)
                await session.commit()

            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                response = await client.post(
                    "/api/admin/cohortes",
                    json={
                        "carrera_id": str(carrera.id),
                        "nombre": "2026-A",
                        "anio": 2026,
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 400
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_list_cohortes_filter_by_carrera(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            carrera = await self._seed_carrera(eng)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                await client.post(
                    "/api/admin/cohortes",
                    json={
                        "carrera_id": str(carrera.id),
                        "nombre": "2026-A",
                        "anio": 2026,
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
                resp = await client.get(
                    f"/api/admin/cohortes?carrera_id={carrera.id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert resp.status_code == 200
            assert resp.json()["total"] == 1
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_soft_delete_cohorte(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            carrera = await self._seed_carrera(eng)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                created = await client.post(
                    "/api/admin/cohortes",
                    json={
                        "carrera_id": str(carrera.id),
                        "nombre": "2026-A",
                        "anio": 2026,
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
                cohorte_id = created.json()["id"]
                response = await client.delete(
                    f"/api/admin/cohortes/{cohorte_id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 204
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_update_cohorte(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            carrera = await self._seed_carrera(eng)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                created = await client.post(
                    "/api/admin/cohortes",
                    json={
                        "carrera_id": str(carrera.id),
                        "nombre": "2026-A",
                        "anio": 2026,
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
                cohorte_id = created.json()["id"]
                response = await client.put(
                    f"/api/admin/cohortes/{cohorte_id}",
                    json={"nombre": "2026-B"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["nombre"] == "2026-B"
        finally:
            await _teardown_db()
            await eng.dispose()


class TestMateriaCrud:
    async def test_create_materia(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                response = await client.post(
                    "/api/admin/materias",
                    json={
                        "codigo": "MAT-101",
                        "nombre": "Matemáticas",
                        "carga_horaria": 120,
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 201
            data = response.json()
            assert data["codigo"] == "MAT-101"
            assert data["nombre"] == "Matemáticas"
            assert data["carga_horaria"] == 120
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_create_materia_without_carrera(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                response = await client.post(
                    "/api/admin/materias",
                    json={
                        "codigo": "MAT-101",
                        "nombre": "Matemáticas",
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 201
            assert response.json()["carrera_id"] is None
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_create_materia_duplicate_codigo(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                await client.post(
                    "/api/admin/materias",
                    json={"codigo": "MAT-101", "nombre": "Matemáticas"},
                    headers={"Authorization": f"Bearer {token}"},
                )
                response = await client.post(
                    "/api/admin/materias",
                    json={"codigo": "MAT-101", "nombre": "Duplicado"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 409
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_materia_multi_tenant_isolation(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng, TENANT_ID, "tenant-a", "TEN_A")
            await _seed_tenant(eng, TENANT2_ID, "tenant-b", "TEN_B")

            user_a = await _seed_user(eng, TENANT_ID, "admin@a.com")
            user_b = await _seed_user(eng, TENANT2_ID, "admin@b.com")
            admin_a = await _seed_role(eng, TENANT_ID, "ADMIN_A", ["estructura:gestionar"])
            admin_b = await _seed_role(eng, TENANT2_ID, "ADMIN_B", ["estructura:gestionar"])
            await _assign_role(eng, user_a.id, admin_a.id, TENANT_ID)
            await _assign_role(eng, user_b.id, admin_b.id, TENANT2_ID)

            token_a = create_access_token(
                {"sub": str(user_a.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN_A"]},
            )
            token_b = create_access_token(
                {"sub": str(user_b.id), "tenant_id": str(TENANT2_ID), "roles": ["ADMIN_B"]},
            )

            async with await _make_app() as client:
                await client.post(
                    "/api/admin/materias",
                    json={"codigo": "MAT-101", "nombre": "Mat A"},
                    headers={"Authorization": f"Bearer {token_a}"},
                )
                resp_b = await client.post(
                    "/api/admin/materias",
                    json={"codigo": "MAT-101", "nombre": "Mat B"},
                    headers={"Authorization": f"Bearer {token_b}"},
                )
                assert resp_b.status_code == 201

                list_a = await client.get(
                    "/api/admin/materias",
                    headers={"Authorization": f"Bearer {token_a}"},
                )
            assert list_a.json()["total"] == 1
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_list_materias_filter_by_carrera(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                carrera = Carrera(
                    id=uuid.uuid4(),
                    tenant_id=TENANT_ID,
                    codigo="CARR",
                    nombre="Carrera",
                    is_active=True,
                )
                session.add(carrera)
                await session.commit()

            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                await client.post(
                    "/api/admin/materias",
                    json={
                        "codigo": "MAT-101",
                        "nombre": "Mat 1",
                        "carrera_id": str(carrera.id),
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
                await client.post(
                    "/api/admin/materias",
                    json={"codigo": "MAT-102", "nombre": "Mat 2"},
                    headers={"Authorization": f"Bearer {token}"},
                )

                resp = await client.get(
                    f"/api/admin/materias?carrera_id={carrera.id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert resp.status_code == 200
            assert resp.json()["total"] == 1
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_soft_delete_materia(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                created = await client.post(
                    "/api/admin/materias",
                    json={"codigo": "MAT-101", "nombre": "To Delete"},
                    headers={"Authorization": f"Bearer {token}"},
                )
                materia_id = created.json()["id"]
                response = await client.delete(
                    f"/api/admin/materias/{materia_id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 204
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_update_materia(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                created = await client.post(
                    "/api/admin/materias",
                    json={"codigo": "MAT-101", "nombre": "Original"},
                    headers={"Authorization": f"Bearer {token}"},
                )
                materia_id = created.json()["id"]
                response = await client.put(
                    f"/api/admin/materias/{materia_id}",
                    json={"nombre": "Updated", "carga_horaria": 80},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["nombre"] == "Updated"
            assert response.json()["carga_horaria"] == 80
        finally:
            await _teardown_db()
            await eng.dispose()


class TestPermissionGuard:
    async def test_authorized_user_passes(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng)
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            async with await _make_app() as client:
                response = await client.get(
                    "/api/admin/carreras",
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
            no_perm_role = await _seed_role(
                eng, name="LIMITED", permissions=["test:read"], system=False,
            )
            await _assign_role(eng, user.id, no_perm_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["LIMITED"]},
            )

            async with await _make_app() as client:
                response = await client.get(
                    "/api/admin/carreras",
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
                    "/api/admin/carreras",
                    json={"codigo": "X", "nombre": "X"},
                )
            assert response.status_code == 401
        finally:
            await _teardown_db()
            await eng.dispose()
