import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
import sqlalchemy as sa
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import close_db_engine
from tests.db_utils import drop_enum_types
from app.models.audit_log import AuditLog
from app.models.comunicacion import Comunicacion
from app.models.materia import Materia
from app.models.tenant import Tenant
from app.models.usuario import Usuario

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


async def _seed_tenant(eng, tenant_id=None):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        tid = tenant_id or TENANT_ID
        tenant = Tenant(
            id=tid,
            name=f"Test Tenant {tid}",
            slug=f"test-tenant-{tid}",
            code=f"TT{tid}",
        )
        session.add(tenant)
        await session.commit()


async def _seed_user(eng, tenant_id=None):
    from app.core.security import hash_password
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        tid = tenant_id or TENANT_ID
        user = Usuario(
            id=uuid.uuid4(),
            tenant_id=tid,
            email=f"user-{uuid.uuid4()}@example.com",
            hashed_password=hash_password("testpass123"),
            is_active=True,
            nombre="Test",
            apellido=f"User-{uuid.uuid4().hex[:4]}",
        )
        session.add(user)
        await session.commit()
        return user


async def _seed_materia(eng, tenant_id=None):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        tid = tenant_id or TENANT_ID
        materia = Materia(
            id=uuid.uuid4(),
            tenant_id=tid,
            codigo=f"MAT-{uuid.uuid4().hex[:4]}",
            nombre="Test Materia",
        )
        session.add(materia)
        await session.commit()
        return materia


async def _seed_audit_log(eng, actor_id, accion="TEST", materia_id=None, days_offset=0, tenant_id=None):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        tid = tenant_id or TENANT_ID
        entry = AuditLog(
            id=uuid.uuid4(),
            tenant_id=tid,
            actor_id=actor_id,
            accion=accion,
            materia_id=materia_id,
            filas_afectadas=1,
            fecha_hora=datetime.now(timezone.utc) - timedelta(days=days_offset),
        )
        session.add(entry)
        await session.commit()


async def _seed_role_with_permission(eng, name, permission):
    from app.models.role import Role
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        role = Role(
            id=uuid.uuid4(),
            tenant_id=TENANT_ID,
            name=name,
            description=name,
            permissions=[permission],
            is_system_role=True,
        )
        session.add(role)
        await session.commit()
        return role.id


async def _assign_role(eng, usuario_id, role_id):
    from app.models.usuario_role import UsuarioRole
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        assignment = UsuarioRole(
            usuario_id=usuario_id,
            role_id=role_id,
            tenant_id=TENANT_ID,
        )
        session.add(assignment)
        await session.commit()


# ===== Group 1: Últimas acciones (Task 5.4) =====


class TestUltimasAcciones:
    async def test_returns_200_entries_by_default(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role_id = await _seed_role_with_permission(eng, "ADMIN", "auditoria:ver")
            await _assign_role(eng, user.id, role_id)
            for i in range(250):
                await _seed_audit_log(eng, user.id, f"ACCION_{i}")

            from app.core.security import create_access_token
            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": ["ADMIN"],
            })
            from app.main import create_app
            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.get(
                    "/api/auditoria/ultimas-acciones",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert len(data["items"]) <= 200
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_accepts_custom_limit(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role_id = await _seed_role_with_permission(eng, "ADMIN", "auditoria:ver")
            await _assign_role(eng, user.id, role_id)
            for i in range(50):
                await _seed_audit_log(eng, user.id, f"ACCION_{i}")
            await _seed_audit_log(eng, user.id, "TARGET", days_offset=1)

            from app.core.security import create_access_token
            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": ["ADMIN"],
            })
            from app.main import create_app
            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.get(
                    "/api/auditoria/ultimas-acciones",
                    params={"limit": 10, "accion": "TARGET"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert len(data["items"]) == 1
            assert data["items"][0]["accion"] == "TARGET"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_rejects_limit_above_500(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role_id = await _seed_role_with_permission(eng, "ADMIN", "auditoria:ver")
            await _assign_role(eng, user.id, role_id)

            from app.core.security import create_access_token
            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": ["ADMIN"],
            })
            from app.main import create_app
            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.get(
                    "/api/auditoria/ultimas-acciones",
                    params={"limit": 1000},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 422
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_requires_permission(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)

            from app.core.security import create_access_token
            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": [],
            })
            from app.main import create_app
            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.get(
                    "/api/auditoria/ultimas-acciones",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()


# ===== Group 2: Acciones por día (Task 5.5) =====


class TestAccionesPorDia:
    async def test_returns_daily_counts(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role_id = await _seed_role_with_permission(eng, "ADMIN", "auditoria:ver")
            await _assign_role(eng, user.id, role_id)
            await _seed_audit_log(eng, user.id, "ACCION_A", days_offset=0)
            await _seed_audit_log(eng, user.id, "ACCION_B", days_offset=1)

            from app.core.security import create_access_token
            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": ["ADMIN"],
            })
            from app.main import create_app
            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.get(
                    "/api/auditoria/metricas/acciones-por-dia",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert len(data["items"]) >= 2
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_filters_by_materia(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            materia = await _seed_materia(eng)
            role_id = await _seed_role_with_permission(eng, "ADMIN", "auditoria:ver")
            await _assign_role(eng, user.id, role_id)
            await _seed_audit_log(eng, user.id, "CON_MATERIA", materia_id=materia.id)
            await _seed_audit_log(eng, user.id, "SIN_MATERIA")

            from app.core.security import create_access_token
            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": ["ADMIN"],
            })
            from app.main import create_app
            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.get(
                    "/api/auditoria/metricas/acciones-por-dia",
                    params={"materia_id": str(materia.id)},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert len(data["items"]) == 1
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_requires_permission(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)

            from app.core.security import create_access_token
            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": [],
            })
            from app.main import create_app
            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.get(
                    "/api/auditoria/metricas/acciones-por-dia",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_tenant_scope(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            await _seed_tenant(eng, TENANT2_ID)
            user = await _seed_user(eng)
            role_id = await _seed_role_with_permission(eng, "ADMIN", "auditoria:ver")
            await _assign_role(eng, user.id, role_id)
            await _seed_audit_log(eng, user.id, "T1", tenant_id=TENANT_ID)
            await _seed_audit_log(eng, user.id, "T2", tenant_id=TENANT2_ID)

            from app.core.security import create_access_token
            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": ["ADMIN"],
            })
            from app.main import create_app
            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.get(
                    "/api/auditoria/metricas/acciones-por-dia",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            for item in data["items"]:
                assert item["fecha"] is not None
        finally:
            await _teardown_db()
            await eng.dispose()


# ===== Group 3: Por docente (Task 5.6) =====


class TestPorDocente:
    async def test_returns_grouped_counts(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role_id = await _seed_role_with_permission(eng, "ADMIN", "auditoria:ver")
            await _assign_role(eng, user.id, role_id)
            for i in range(3):
                await _seed_audit_log(eng, user.id, "ACCION_A")
            await _seed_audit_log(eng, user.id, "ACCION_B")

            from app.core.security import create_access_token
            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": ["ADMIN"],
            })
            from app.main import create_app
            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.get(
                    "/api/auditoria/metricas/por-docente",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert len(data["items"]) == 1
            assert data["items"][0]["total"] == 4
            assert "ACCION_A" in data["items"][0]["detalle_por_accion"]
            assert "ACCION_B" in data["items"][0]["detalle_por_accion"]
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_requires_permission(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)

            from app.core.security import create_access_token
            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": [],
            })
            from app.main import create_app
            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.get(
                    "/api/auditoria/metricas/por-docente",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()


# ===== Group 4: Por materia (Task 5.7) =====


class TestPorMateria:
    async def test_returns_docente_materia_counts(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            materia = await _seed_materia(eng)
            role_id = await _seed_role_with_permission(eng, "ADMIN", "auditoria:ver")
            await _assign_role(eng, user.id, role_id)
            for i in range(3):
                await _seed_audit_log(eng, user.id, "TEST", materia_id=materia.id)

            from app.core.security import create_access_token
            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": ["ADMIN"],
            })
            from app.main import create_app
            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.get(
                    "/api/auditoria/metricas/por-materia",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert len(data["items"]) >= 1
            for item in data["items"]:
                assert item["total"] >= 1
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_requires_permission(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)

            from app.core.security import create_access_token
            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": [],
            })
            from app.main import create_app
            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.get(
                    "/api/auditoria/metricas/por-materia",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()


# ===== Group 5: Comunicaciones (Task 5.8) =====


class TestComunicaciones:
    async def test_returns_state_breakdown(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            materia = await _seed_materia(eng)
            role_id = await _seed_role_with_permission(eng, "ADMIN", "auditoria:ver")
            await _assign_role(eng, user.id, role_id)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                for estado in ["Pendiente", "Enviado", "Pendiente"]:
                    com = Comunicacion(
                        tenant_id=TENANT_ID,
                        enviado_por_id=user.id,
                        materia_id=materia.id,
                        lote_id=uuid.uuid4(),
                        destinatario="test@test.com",
                        asunto="Test",
                        cuerpo="Test body",
                        estado=estado,
                    )
                    session.add(com)
                await session.commit()

            from app.core.security import create_access_token
            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": ["ADMIN"],
            })
            from app.main import create_app
            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.get(
                    "/api/auditoria/metricas/comunicaciones",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert len(data["items"]) == 1
            estados = data["items"][0]["estados"]
            assert estados["Pendiente"] == 2
            assert estados["Enviado"] == 1
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_requires_permission(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)

            from app.core.security import create_access_token
            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": [],
            })
            from app.main import create_app
            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.get(
                    "/api/auditoria/metricas/comunicaciones",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_tenant_scope(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            await _seed_tenant(eng, TENANT2_ID)
            user = await _seed_user(eng)
            materia = await _seed_materia(eng)
            role_id = await _seed_role_with_permission(eng, "ADMIN", "auditoria:ver")
            await _assign_role(eng, user.id, role_id)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                com1 = Comunicacion(
                    tenant_id=TENANT_ID,
                    enviado_por_id=user.id,
                    materia_id=materia.id,
                    lote_id=uuid.uuid4(),
                    destinatario="t1@test.com",
                    asunto="T1",
                    cuerpo="Body",
                    estado="Enviado",
                )
                com2 = Comunicacion(
                    tenant_id=TENANT2_ID,
                    enviado_por_id=user.id,
                    materia_id=materia.id,
                    lote_id=uuid.uuid4(),
                    destinatario="t2@test.com",
                    asunto="T2",
                    cuerpo="Body",
                    estado="Pendiente",
                )
                session.add(com1)
                session.add(com2)
                await session.commit()

            from app.core.security import create_access_token
            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": ["ADMIN"],
            })
            from app.main import create_app
            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.get(
                    "/api/auditoria/metricas/comunicaciones",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert len(data["items"]) == 1
            assert "Enviado" in data["items"][0]["estados"]
        finally:
            await _teardown_db()
            await eng.dispose()
