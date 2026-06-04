"""Integration tests for equipos docentes endpoints (C-08)."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base, close_db_engine
from app.core.security import create_access_token, hash_password
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.models.role import Role
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.models.usuario_role import UsuarioRole

pytestmark = pytest.mark.asyncio

DB_URL = "postgresql+asyncpg://active_trace:active_trace@localhost:5432/active_trace_test"
TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
TENANT2_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


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


async def _seed_tenant(eng, tenant_id=TENANT_ID, slug="test-tenant", code="TEST"):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        existing = await session.get(Tenant, tenant_id)
        if existing is None:
            tenant = Tenant(id=tenant_id, name="Test", slug=slug, code=code)
            session.add(tenant)
            await session.commit()


async def _seed_user(eng, tenant_id=TENANT_ID, email="coord@test.com", nombre="Carlos", apellido="Garcia"):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        user = Usuario(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            email=email,
            hashed_password=hash_password("testpass123"),
            is_active=True,
            nombre=nombre,
            apellido=apellido,
        )
        session.add(user)
        await session.commit()
        return user


async def _seed_role(eng, tenant_id=TENANT_ID, name="COORDINADOR", permissions=None, system=True):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        role = Role(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name=name,
            permissions=permissions or ["equipos:ver", "equipos:asignar"],
            is_system_role=system,
        )
        session.add(role)
        await session.commit()
        return role


async def _seed_role_no_permission(eng, tenant_id=TENANT_ID):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        role = Role(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name="ALUMNO",
            permissions=[],
            is_system_role=True,
        )
        session.add(role)
        await session.commit()
        return role


async def _seed_role_ver_only(eng, tenant_id=TENANT_ID):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        role = Role(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name="PROFESOR",
            permissions=["equipos:ver"],
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
            codigo=f"CARR-{uuid.uuid4().hex[:6]}",
            nombre="Ingenieria",
            is_active=True,
        )
        session.add(carrera)
        await session.commit()
        return carrera


async def _seed_cohorte(eng, tenant_id=TENANT_ID, carrera_id=None, nombre=None):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        cohorte = Cohorte(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            carrera_id=carrera_id or uuid.uuid4(),
            nombre=nombre or uuid.uuid4().hex[:8],
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
            nombre="Matematica",
            is_active=True,
        )
        session.add(materia)
        await session.commit()
        return materia


async def _seed_asignacion(
    eng,
    tenant_id=TENANT_ID,
    usuario_id=None,
    materia_id=None,
    carrera_id=None,
    cohorte_id=None,
    rol="PROFESOR",
):
    from app.models.asignacion import Asignacion
    from datetime import date
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        asig = Asignacion(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            usuario_id=usuario_id or uuid.uuid4(),
            rol=rol,
            carrera_id=carrera_id,
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            fecha_inicio=date(2026, 1, 1),
            fecha_fin=date(2026, 12, 31),
            comisiones=["A"],
        )
        session.add(asig)
        await session.commit()
        return asig


async def _build_test_data(eng, tenant_id=TENANT_ID, role_name="COORDINADOR", permissions=None):
    await _seed_tenant(eng, tenant_id)
    carrera = await _seed_carrera(eng, tenant_id)
    cohorte = await _seed_cohorte(eng, tenant_id, carrera.id)
    materia = await _seed_materia(eng, tenant_id)
    user = await _seed_user(eng, tenant_id)
    role = await _seed_role(eng, tenant_id, name=role_name, permissions=permissions)
    await _assign_role(eng, user.id, role.id, tenant_id)
    return user, materia, cohorte, carrera


async def _make_app():
    from app.main import create_app
    app = create_app()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


# ── Task 7.1: GET /api/equipos/mis-equipos ─────────────────────────────────


class TestMisEquipos:
    async def test_mis_equipos_happy_path(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            user, materia, cohorte, carrera = await _build_test_data(eng)
            await _seed_asignacion(eng, TENANT_ID, user.id, materia.id, carrera.id, cohorte.id, "PROFESOR")
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            async with await _make_app() as client:
                response = await client.get(
                    "/api/equipos/mis-equipos",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert len(data["items"]) == 1
            assert data["items"][0]["rol"] == "PROFESOR"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_mis_equipos_filter_by_estado_vigente(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            from datetime import date
            await _setup_db()
            user, materia, cohorte, carrera = await _build_test_data(eng)
            await _seed_asignacion(eng, TENANT_ID, user.id, materia.id, carrera.id, cohorte.id, "PROFESOR")
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            async with await _make_app() as client:
                response = await client.get(
                    "/api/equipos/mis-equipos?estado=vigente",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["total"] == 1
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_mis_equipos_empty_results(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            user, _, _, _ = await _build_test_data(eng)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            async with await _make_app() as client:
                response = await client.get(
                    "/api/equipos/mis-equipos",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 0
            assert data["items"] == []
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_mis_equipos_403_without_permission(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role_no_permission(eng)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ALUMNO"]},
            )
            async with await _make_app() as client:
                response = await client.get(
                    "/api/equipos/mis-equipos",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()


# ── Task 7.2: GET /api/equipos ──────────────────────────────────────────


class TestListEquipos:
    async def test_list_equipos_full_list(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            user, materia, cohorte, carrera = await _build_test_data(eng)
            await _seed_asignacion(eng, TENANT_ID, user.id, materia.id, carrera.id, cohorte.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            async with await _make_app() as client:
                response = await client.get(
                    "/api/equipos",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert data["total"] >= 1
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_list_equipos_filtered_by_materia(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            user, materia, cohorte, carrera = await _build_test_data(eng)
            await _seed_asignacion(eng, TENANT_ID, user.id, materia.id, carrera.id, cohorte.id)
            materia2 = await _seed_materia(eng)
            await _seed_asignacion(eng, TENANT_ID, user.id, materia2.id, carrera.id, cohorte.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            async with await _make_app() as client:
                response = await client.get(
                    f"/api/equipos?materia_id={materia.id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["total"] == 1
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_list_equipos_filtered_by_carrera(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            user, materia, cohorte, carrera = await _build_test_data(eng)
            await _seed_asignacion(eng, TENANT_ID, user.id, materia.id, carrera.id, cohorte.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            async with await _make_app() as client:
                response = await client.get(
                    f"/api/equipos?carrera_id={carrera.id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["total"] == 1
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_list_equipos_tenant_isolation(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng, TENANT_ID, "t1", "T1")
            await _seed_tenant(eng, TENANT2_ID, "t2", "T2")
            user1, materia1, cohorte1, carrera1 = await _build_test_data(eng, TENANT_ID)
            await _seed_asignacion(eng, TENANT_ID, user1.id, materia1.id, carrera1.id, cohorte1.id)
            user2 = await _seed_user(eng, TENANT2_ID, "coord2@test.com")
            role2 = await _seed_role(eng, TENANT2_ID, "COORDINADOR", ["equipos:ver", "equipos:asignar"])
            await _assign_role(eng, user2.id, role2.id, TENANT2_ID)
            token = create_access_token(
                {"sub": str(user2.id), "tenant_id": str(TENANT2_ID), "roles": ["COORDINADOR"]},
            )
            async with await _make_app() as client:
                response = await client.get(
                    "/api/equipos",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["total"] == 0
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_list_equipos_403_without_permission(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role_no_permission(eng)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ALUMNO"]},
            )
            async with await _make_app() as client:
                response = await client.get(
                    "/api/equipos",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()


# ── Task 7.3: POST /api/equipos/asignacion-masiva ───────────────────────


class TestAsignacionMasiva:
    async def test_asignacion_masiva_success(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            user, materia, cohorte, carrera = await _build_test_data(eng)
            docentes = [await _seed_user(eng, TENANT_ID, f"doc{i}@test.com") for i in range(3)]
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            body = {
                "usuario_ids": [str(d.id) for d in docentes],
                "materia_id": str(materia.id),
                "carrera_id": str(carrera.id),
                "cohorte_id": str(cohorte.id),
                "rol": "PROFESOR",
                "fecha_inicio": "2026-03-01",
                "fecha_fin": "2026-07-31",
            }
            async with await _make_app() as client:
                response = await client.post(
                    "/api/equipos/asignacion-masiva",
                    json=body,
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 201
            assert response.json()["creadas"] == 3
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_asignacion_masiva_invalid_usuario_rollback(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            user, materia, cohorte, carrera = await _build_test_data(eng)
            docentes = [await _seed_user(eng, TENANT_ID, f"doc{i}@test.com") for i in range(2)]
            fake_id = uuid.uuid4()
            usuario_ids = [str(d.id) for d in docentes] + [str(fake_id)]
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            body = {
                "usuario_ids": usuario_ids,
                "materia_id": str(materia.id),
                "carrera_id": str(carrera.id),
                "cohorte_id": str(cohorte.id),
                "rol": "PROFESOR",
                "fecha_inicio": "2026-03-01",
                "fecha_fin": "2026-07-31",
            }
            async with await _make_app() as client:
                response = await client.post(
                    "/api/equipos/asignacion-masiva",
                    json=body,
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 400
            assert "not found" in response.json()["detail"]
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_asignacion_masiva_with_responsable(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            user, materia, cohorte, carrera = await _build_test_data(eng)
            docente = await _seed_user(eng, TENANT_ID, "doc@test.com")
            responsable = await _seed_user(eng, TENANT_ID, "resp@test.com")
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            body = {
                "usuario_ids": [str(docente.id)],
                "materia_id": str(materia.id),
                "carrera_id": str(carrera.id),
                "cohorte_id": str(cohorte.id),
                "rol": "PROFESOR",
                "responsable_id": str(responsable.id),
                "fecha_inicio": "2026-03-01",
                "fecha_fin": "2026-07-31",
            }
            async with await _make_app() as client:
                response = await client.post(
                    "/api/equipos/asignacion-masiva",
                    json=body,
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 201
            assert response.json()["creadas"] == 1
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_asignacion_masiva_403_without_permission(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role_ver_only(eng)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["PROFESOR"]},
            )
            body = {
                "usuario_ids": [str(uuid.uuid4())],
                "materia_id": str(uuid.uuid4()),
                "carrera_id": str(uuid.uuid4()),
                "cohorte_id": str(uuid.uuid4()),
                "rol": "PROFESOR",
                "fecha_inicio": "2026-03-01",
                "fecha_fin": "2026-07-31",
            }
            async with await _make_app() as client:
                response = await client.post(
                    "/api/equipos/asignacion-masiva",
                    json=body,
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()


# ── Task 7.4: POST /api/equipos/clonar ────────────────────────────────


class TestClonar:
    async def test_clonar_success_with_n_copies(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            user, materia, cohorte, carrera = await _build_test_data(eng)
            cohorte_destino = await _seed_cohorte(eng, TENANT_ID, carrera.id)
            await _seed_asignacion(eng, TENANT_ID, user.id, materia.id, carrera.id, cohorte.id, "PROFESOR")
            await _seed_asignacion(eng, TENANT_ID, user.id, materia.id, carrera.id, cohorte.id, "TUTOR")
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            body = {
                "materia_id": str(materia.id),
                "carrera_id": str(carrera.id),
                "cohorte_origen_id": str(cohorte.id),
                "cohorte_destino_id": str(cohorte_destino.id),
                "fecha_inicio": "2026-08-01",
                "fecha_fin": "2026-12-31",
            }
            async with await _make_app() as client:
                response = await client.post(
                    "/api/equipos/clonar",
                    json=body,
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["creadas"] == 2
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_clonar_empty_source(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            user, materia, cohorte, carrera = await _build_test_data(eng)
            cohorte_destino = await _seed_cohorte(eng, TENANT_ID, carrera.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            body = {
                "materia_id": str(materia.id),
                "carrera_id": str(carrera.id),
                "cohorte_origen_id": str(cohorte.id),
                "cohorte_destino_id": str(cohorte_destino.id),
                "fecha_inicio": "2026-08-01",
                "fecha_fin": "2026-12-31",
            }
            async with await _make_app() as client:
                response = await client.post(
                    "/api/equipos/clonar",
                    json=body,
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["creadas"] == 0
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_clonar_invalid_destino_cohorte(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            user, materia, cohorte, carrera = await _build_test_data(eng)
            fake_cohorte_id = uuid.uuid4()
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            body = {
                "materia_id": str(materia.id),
                "carrera_id": str(carrera.id),
                "cohorte_origen_id": str(cohorte.id),
                "cohorte_destino_id": str(fake_cohorte_id),
                "fecha_inicio": "2026-08-01",
                "fecha_fin": "2026-12-31",
            }
            async with await _make_app() as client:
                response = await client.post(
                    "/api/equipos/clonar",
                    json=body,
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 400
        finally:
            await _teardown_db()
            await eng.dispose()


# ── Task 7.5: PATCH /api/equipos/vigencia ─────────────────────────────


class TestUpdateVigencia:
    async def test_update_vigencia_success(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            user, materia, cohorte, carrera = await _build_test_data(eng)
            await _seed_asignacion(eng, TENANT_ID, user.id, materia.id, carrera.id, cohorte.id, "PROFESOR")
            await _seed_asignacion(eng, TENANT_ID, user.id, materia.id, carrera.id, cohorte.id, "TUTOR")
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            body = {
                "materia_id": str(materia.id),
                "carrera_id": str(carrera.id),
                "cohorte_id": str(cohorte.id),
                "fecha_inicio": "2026-08-15",
                "fecha_fin": "2026-12-20",
            }
            async with await _make_app() as client:
                response = await client.patch(
                    "/api/equipos/vigencia",
                    json=body,
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["afectadas"] == 2
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_update_vigencia_empty_scope(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            user, materia, cohorte, carrera = await _build_test_data(eng)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            body = {
                "materia_id": str(materia.id),
                "carrera_id": str(carrera.id),
                "cohorte_id": str(cohorte.id),
                "fecha_inicio": "2026-08-15",
                "fecha_fin": "2026-12-20",
            }
            async with await _make_app() as client:
                response = await client.patch(
                    "/api/equipos/vigencia",
                    json=body,
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["afectadas"] == 0
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_update_vigencia_403_without_permission(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role_ver_only(eng)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["PROFESOR"]},
            )
            body = {
                "materia_id": str(uuid.uuid4()),
                "carrera_id": str(uuid.uuid4()),
                "cohorte_id": str(uuid.uuid4()),
                "fecha_inicio": "2026-08-15",
                "fecha_fin": "2026-12-20",
            }
            async with await _make_app() as client:
                response = await client.patch(
                    "/api/equipos/vigencia",
                    json=body,
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()


# ── Task 7.6: GET /api/equipos/exportar ───────────────────────────────


class TestExportar:
    async def test_exportar_csv_content_format(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            user, materia, cohorte, carrera = await _build_test_data(eng)
            await _seed_asignacion(eng, TENANT_ID, user.id, materia.id, carrera.id, cohorte.id, "PROFESOR")
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            async with await _make_app() as client:
                response = await client.get(
                    f"/api/equipos/exportar?materia_id={materia.id}&carrera_id={carrera.id}&cohorte_id={cohorte.id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert "text/csv" in response.headers["content-type"]
            assert "attachment" in response.headers["content-disposition"]
            assert "docente" in response.text
            assert "PROFESOR" in response.text
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_exportar_empty_result_header_only(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            user, materia, cohorte, carrera = await _build_test_data(eng)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            async with await _make_app() as client:
                response = await client.get(
                    f"/api/equipos/exportar?materia_id={materia.id}&carrera_id={carrera.id}&cohorte_id={cohorte.id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert "docente" in response.text
            lines = response.text.strip().split("\n")
            assert len(lines) == 1
        finally:
            await _teardown_db()
            await eng.dispose()
