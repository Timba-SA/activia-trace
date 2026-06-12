"""Integration tests for avisos endpoints."""
import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base, close_db_engine
from app.core.security import create_access_token, hash_password
from app.models.aviso import Aviso, AlcanceAviso, SeveridadAviso
from app.models.role import Role
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.models.usuario_role import UsuarioRole

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


async def _seed_tenant(eng, tenant_id=TENANT_ID, slug="test-tenant"):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        tenant = Tenant(id=tenant_id, name="Test", slug=slug, code="TEST")
        session.add(tenant)
        await session.commit()


async def _seed_user(eng, tenant_id=TENANT_ID, email="user@test.com", password="testpass123"):
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


async def _seed_role(eng, tenant_id=TENANT_ID, name="COORDINADOR", permissions=None):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        role = Role(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name=name,
            permissions=permissions or [],
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


async def _make_app():
    from app.main import create_app
    app = create_app()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


def _now():
    return datetime.now(timezone.utc)


class TestAvisosCrud:
    async def test_create_aviso(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["avisos:publicar"])
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            now = _now()
            async with await _make_app() as client:
                response = await client.post(
                    "/api/avisos/",
                    json={
                        "alcance": "Global",
                        "severidad": "Info",
                        "titulo": "Aviso importante",
                        "cuerpo": "Este es un aviso de prueba",
                        "inicio_en": now.isoformat(),
                        "fin_en": (now + timedelta(days=7)).isoformat(),
                        "orden": 1,
                        "activo": True,
                        "requiere_ack": False,
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 201
            data = response.json()
            assert data["titulo"] == "Aviso importante"
            assert data["alcance"] == "Global"
            assert data["severidad"] == "Info"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_list_avisos(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["avisos:publicar"])
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            now = _now()
            async with await _make_app() as client:
                await client.post(
                    "/api/avisos/",
                    json={
                        "alcance": "Global",
                        "severidad": "Info",
                        "titulo": "Aviso 1",
                        "cuerpo": "Cuerpo 1",
                        "inicio_en": now.isoformat(),
                        "fin_en": (now + timedelta(days=7)).isoformat(),
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
                await client.post(
                    "/api/avisos/",
                    json={
                        "alcance": "PorRol",
                        "severidad": "Advertencia",
                        "titulo": "Aviso 2",
                        "cuerpo": "Cuerpo 2",
                        "rol_destino": "PROFESOR",
                        "inicio_en": now.isoformat(),
                        "fin_en": (now + timedelta(days=7)).isoformat(),
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )

                response = await client.get(
                    "/api/avisos/",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 2
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_update_aviso(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["avisos:publicar"])
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            now = _now()
            async with await _make_app() as client:
                created = await client.post(
                    "/api/avisos/",
                    json={
                        "alcance": "Global",
                        "severidad": "Info",
                        "titulo": "Original",
                        "cuerpo": "Cuerpo original",
                        "inicio_en": now.isoformat(),
                        "fin_en": (now + timedelta(days=7)).isoformat(),
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
                aviso_id = created.json()["id"]

                response = await client.patch(
                    f"/api/avisos/{aviso_id}",
                    json={"titulo": "Actualizado"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["titulo"] == "Actualizado"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_delete_aviso(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["avisos:publicar"])
            await _assign_role(eng, user.id, admin_role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )

            now = _now()
            async with await _make_app() as client:
                created = await client.post(
                    "/api/avisos/",
                    json={
                        "alcance": "Global",
                        "severidad": "Info",
                        "titulo": "A eliminar",
                        "cuerpo": "Cuerpo",
                        "inicio_en": now.isoformat(),
                        "fin_en": (now + timedelta(days=7)).isoformat(),
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
                aviso_id = created.json()["id"]

                response = await client.delete(
                    f"/api/avisos/{aviso_id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 204
        finally:
            await _teardown_db()
            await eng.dispose()


class TestMisAvisos:
    async def test_global_aviso_appears_for_alumno(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            admin = await _seed_user(eng, email="admin@test.com")
            alumno = await _seed_user(eng, email="alumno@test.com")
            admin_role = await _seed_role(eng, permissions=["avisos:publicar"])
            alumno_role = await _seed_role(eng, name="ALUMNO", permissions=[])
            await _assign_role(eng, admin.id, admin_role.id)
            await _assign_role(eng, alumno.id, alumno_role.id)

            admin_token = create_access_token(
                {"sub": str(admin.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )
            alumno_token = create_access_token(
                {"sub": str(alumno.id), "tenant_id": str(TENANT_ID), "roles": ["ALUMNO"]},
            )

            now = _now()
            async with await _make_app() as client:
                await client.post(
                    "/api/avisos/",
                    json={
                        "alcance": "Global",
                        "severidad": "Info",
                        "titulo": "Aviso Global",
                        "cuerpo": "Para todos",
                        "inicio_en": now.isoformat(),
                        "fin_en": (now + timedelta(days=7)).isoformat(),
                    },
                    headers={"Authorization": f"Bearer {admin_token}"},
                )

                response = await client.get(
                    "/api/avisos/mis-avisos",
                    headers={"Authorization": f"Bearer {alumno_token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_por_rol_aviso_filters_by_role(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            admin = await _seed_user(eng, email="admin@test.com")
            profesor = await _seed_user(eng, email="profesor@test.com")
            alumno = await _seed_user(eng, email="alumno@test.com")
            admin_role = await _seed_role(eng, permissions=["avisos:publicar"])
            prof_role = await _seed_role(eng, name="PROFESOR", permissions=[])
            alumno_role = await _seed_role(eng, name="ALUMNO", permissions=[])
            await _assign_role(eng, admin.id, admin_role.id)
            await _assign_role(eng, profesor.id, prof_role.id)
            await _assign_role(eng, alumno.id, alumno_role.id)

            admin_token = create_access_token(
                {"sub": str(admin.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )
            prof_token = create_access_token(
                {"sub": str(profesor.id), "tenant_id": str(TENANT_ID), "roles": ["PROFESOR"]},
            )
            alumno_token = create_access_token(
                {"sub": str(alumno.id), "tenant_id": str(TENANT_ID), "roles": ["ALUMNO"]},
            )

            now = _now()
            async with await _make_app() as client:
                await client.post(
                    "/api/avisos/",
                    json={
                        "alcance": "PorRol",
                        "severidad": "Info",
                        "titulo": "Solo profesores",
                        "cuerpo": "Test",
                        "rol_destino": "PROFESOR",
                        "inicio_en": now.isoformat(),
                        "fin_en": (now + timedelta(days=7)).isoformat(),
                    },
                    headers={"Authorization": f"Bearer {admin_token}"},
                )

                prof_resp = await client.get(
                    "/api/avisos/mis-avisos",
                    headers={"Authorization": f"Bearer {prof_token}"},
                )
                alumno_resp = await client.get(
                    "/api/avisos/mis-avisos",
                    headers={"Authorization": f"Bearer {alumno_token}"},
                )
            assert prof_resp.json()["total"] == 1
            assert alumno_resp.json()["total"] == 0
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_aviso_outside_vigencia_excluded(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            admin = await _seed_user(eng, email="admin@test.com")
            alumno = await _seed_user(eng, email="alumno@test.com")
            admin_role = await _seed_role(eng, permissions=["avisos:publicar"])
            alumno_role = await _seed_role(eng, name="ALUMNO", permissions=[])
            await _assign_role(eng, admin.id, admin_role.id)
            await _assign_role(eng, alumno.id, alumno_role.id)

            admin_token = create_access_token(
                {"sub": str(admin.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )
            alumno_token = create_access_token(
                {"sub": str(alumno.id), "tenant_id": str(TENANT_ID), "roles": ["ALUMNO"]},
            )

            now = _now()
            past = now - timedelta(days=10)
            async with await _make_app() as client:
                await client.post(
                    "/api/avisos/",
                    json={
                        "alcance": "Global",
                        "severidad": "Info",
                        "titulo": "Vencido",
                        "cuerpo": "Test",
                        "inicio_en": (now - timedelta(days=20)).isoformat(),
                        "fin_en": past.isoformat(),
                    },
                    headers={"Authorization": f"Bearer {admin_token}"},
                )

                response = await client.get(
                    "/api/avisos/mis-avisos",
                    headers={"Authorization": f"Bearer {alumno_token}"},
                )
            assert response.json()["total"] == 0
        finally:
            await _teardown_db()
            await eng.dispose()


class TestAcknowledgments:
    async def test_confirmar_lectura_exitoso(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            admin = await _seed_user(eng, email="admin@test.com")
            alumno = await _seed_user(eng, email="alumno@test.com")
            admin_role = await _seed_role(eng, permissions=["avisos:publicar"])
            alumno_role = await _seed_role(eng, name="ALUMNO", permissions=[])
            await _assign_role(eng, admin.id, admin_role.id)
            await _assign_role(eng, alumno.id, alumno_role.id)

            admin_token = create_access_token(
                {"sub": str(admin.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )
            alumno_token = create_access_token(
                {"sub": str(alumno.id), "tenant_id": str(TENANT_ID), "roles": ["ALUMNO"]},
            )

            now = _now()
            async with await _make_app() as client:
                created = await client.post(
                    "/api/avisos/",
                    json={
                        "alcance": "Global",
                        "severidad": "Info",
                        "titulo": "Requiere ack",
                        "cuerpo": "Test",
                        "inicio_en": now.isoformat(),
                        "fin_en": (now + timedelta(days=7)).isoformat(),
                        "requiere_ack": True,
                    },
                    headers={"Authorization": f"Bearer {admin_token}"},
                )
                aviso_id = created.json()["id"]

                response = await client.post(
                    f"/api/avisos/{aviso_id}/ack",
                    headers={"Authorization": f"Bearer {alumno_token}"},
                )
            assert response.status_code == 200
            assert response.json()["message"] == "Lectura confirmada"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_ack_duplicado_idempotente(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            admin = await _seed_user(eng, email="admin@test.com")
            alumno = await _seed_user(eng, email="alumno@test.com")
            admin_role = await _seed_role(eng, permissions=["avisos:publicar"])
            alumno_role = await _seed_role(eng, name="ALUMNO", permissions=[])
            await _assign_role(eng, admin.id, admin_role.id)
            await _assign_role(eng, alumno.id, alumno_role.id)

            admin_token = create_access_token(
                {"sub": str(admin.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )
            alumno_token = create_access_token(
                {"sub": str(alumno.id), "tenant_id": str(TENANT_ID), "roles": ["ALUMNO"]},
            )

            now = _now()
            async with await _make_app() as client:
                created = await client.post(
                    "/api/avisos/",
                    json={
                        "alcance": "Global",
                        "severidad": "Info",
                        "titulo": "Ack duplicado",
                        "cuerpo": "Test",
                        "inicio_en": now.isoformat(),
                        "fin_en": (now + timedelta(days=7)).isoformat(),
                        "requiere_ack": True,
                    },
                    headers={"Authorization": f"Bearer {admin_token}"},
                )
                aviso_id = created.json()["id"]

                resp1 = await client.post(
                    f"/api/avisos/{aviso_id}/ack",
                    headers={"Authorization": f"Bearer {alumno_token}"},
                )
                resp2 = await client.post(
                    f"/api/avisos/{aviso_id}/ack",
                    headers={"Authorization": f"Bearer {alumno_token}"},
                )
            assert resp1.status_code == 200
            assert resp2.status_code == 200
            assert resp2.json()["message"] == "Lectura confirmada"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_ack_sin_requiere_ack_return_409(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            admin = await _seed_user(eng, email="admin@test.com")
            alumno = await _seed_user(eng, email="alumno@test.com")
            admin_role = await _seed_role(eng, permissions=["avisos:publicar"])
            alumno_role = await _seed_role(eng, name="ALUMNO", permissions=[])
            await _assign_role(eng, admin.id, admin_role.id)
            await _assign_role(eng, alumno.id, alumno_role.id)

            admin_token = create_access_token(
                {"sub": str(admin.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )
            alumno_token = create_access_token(
                {"sub": str(alumno.id), "tenant_id": str(TENANT_ID), "roles": ["ALUMNO"]},
            )

            now = _now()
            async with await _make_app() as client:
                created = await client.post(
                    "/api/avisos/",
                    json={
                        "alcance": "Global",
                        "severidad": "Info",
                        "titulo": "Sin ack",
                        "cuerpo": "Test",
                        "inicio_en": now.isoformat(),
                        "fin_en": (now + timedelta(days=7)).isoformat(),
                        "requiere_ack": False,
                    },
                    headers={"Authorization": f"Bearer {admin_token}"},
                )
                aviso_id = created.json()["id"]

                response = await client.post(
                    f"/api/avisos/{aviso_id}/ack",
                    headers={"Authorization": f"Bearer {alumno_token}"},
                )
            assert response.status_code == 409
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_obtener_stats(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            admin = await _seed_user(eng, email="admin@test.com")
            alumno1 = await _seed_user(eng, email="alumno1@test.com")
            alumno2 = await _seed_user(eng, email="alumno2@test.com")
            admin_role = await _seed_role(eng, permissions=["avisos:publicar"])
            alumno_role = await _seed_role(eng, name="ALUMNO", permissions=[])
            await _assign_role(eng, admin.id, admin_role.id)
            await _assign_role(eng, alumno1.id, alumno_role.id)
            await _assign_role(eng, alumno2.id, alumno_role.id)

            admin_token = create_access_token(
                {"sub": str(admin.id), "tenant_id": str(TENANT_ID), "roles": ["ADMIN"]},
            )
            token1 = create_access_token(
                {"sub": str(alumno1.id), "tenant_id": str(TENANT_ID), "roles": ["ALUMNO"]},
            )
            token2 = create_access_token(
                {"sub": str(alumno2.id), "tenant_id": str(TENANT_ID), "roles": ["ALUMNO"]},
            )

            now = _now()
            async with await _make_app() as client:
                created = await client.post(
                    "/api/avisos/",
                    json={
                        "alcance": "Global",
                        "severidad": "Info",
                        "titulo": "Stats test",
                        "cuerpo": "Test",
                        "inicio_en": now.isoformat(),
                        "fin_en": (now + timedelta(days=7)).isoformat(),
                        "requiere_ack": True,
                    },
                    headers={"Authorization": f"Bearer {admin_token}"},
                )
                aviso_id = created.json()["id"]

                await client.post(
                    f"/api/avisos/{aviso_id}/ack",
                    headers={"Authorization": f"Bearer {token1}"},
                )
                await client.post(
                    f"/api/avisos/{aviso_id}/ack",
                    headers={"Authorization": f"Bearer {token2}"},
                )

                response = await client.get(
                    f"/api/avisos/{aviso_id}/stats",
                    headers={"Authorization": f"Bearer {admin_token}"},
                )
            assert response.status_code == 200
            assert response.json()["total_confirmaciones"] == 2
        finally:
            await _teardown_db()
            await eng.dispose()


class TestPermissionGuard:
    async def test_alumno_no_puede_publicar(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            alumno = await _seed_user(eng, email="alumno@test.com")
            alumno_role = await _seed_role(eng, name="ALUMNO", permissions=[])
            await _assign_role(eng, alumno.id, alumno_role.id)
            token = create_access_token(
                {"sub": str(alumno.id), "tenant_id": str(TENANT_ID), "roles": ["ALUMNO"]},
            )

            async with await _make_app() as client:
                response = await client.get(
                    "/api/avisos/",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_alumno_puede_ver_mis_avisos(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            alumno = await _seed_user(eng, email="alumno@test.com")
            alumno_role = await _seed_role(eng, name="ALUMNO", permissions=[])
            await _assign_role(eng, alumno.id, alumno_role.id)
            token = create_access_token(
                {"sub": str(alumno.id), "tenant_id": str(TENANT_ID), "roles": ["ALUMNO"]},
            )

            async with await _make_app() as client:
                response = await client.get(
                    "/api/avisos/mis-avisos",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_coordinador_puede_publicar(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            coord = await _seed_user(eng, email="coord@test.com")
            coord_role = await _seed_role(eng, permissions=["avisos:publicar"])
            await _assign_role(eng, coord.id, coord_role.id)
            token = create_access_token(
                {"sub": str(coord.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )

            now = _now()
            async with await _make_app() as client:
                response = await client.post(
                    "/api/avisos/",
                    json={
                        "alcance": "Global",
                        "severidad": "Info",
                        "titulo": "Desde coordinador",
                        "cuerpo": "Test",
                        "inicio_en": now.isoformat(),
                        "fin_en": (now + timedelta(days=7)).isoformat(),
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 201
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_alumno_no_puede_ver_stats(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            alumno = await _seed_user(eng, email="alumno@test.com")
            alumno_role = await _seed_role(eng, name="ALUMNO", permissions=[])
            await _assign_role(eng, alumno.id, alumno_role.id)
            token = create_access_token(
                {"sub": str(alumno.id), "tenant_id": str(TENANT_ID), "roles": ["ALUMNO"]},
            )

            async with await _make_app() as client:
                response = await client.get(
                    f"/api/avisos/{uuid.uuid4()}/stats",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()
