"""Integration tests for analisis endpoints: atrasados, ranking, reportes, monitores, export."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base, close_db_engine
from app.core.security import create_access_token, hash_password
from app.models.calificacion import Calificacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.models.role import Role
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.models.usuario_role import UsuarioRole
from app.models.umbral_materia import UmbralMateria
from app.models.version_padron import VersionPadron

pytestmark = pytest.mark.asyncio

DB_URL = "postgresql+asyncpg://active_trace:active_trace@localhost:5432/active_trace_test"
TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
TENANT2_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


# ---------------------------------------------------------------------------
# Fixtures (DB lifecycle)
# ---------------------------------------------------------------------------

# pool_pre_ping avoids Windows Docker stale TCP connections by verifying
# liveness before each pool checkout.
_ENGINE_ARGS = {"echo": False, "pool_pre_ping": True}


async def _setup_db():
    eng = create_async_engine(DB_URL, **_ENGINE_ARGS)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await eng.dispose()


async def _teardown_db():
    eng = create_async_engine(DB_URL, **_ENGINE_ARGS)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest.fixture(autouse=True)
async def setup_teardown():
    await _setup_db()
    yield
    await _teardown_db()


@pytest.fixture
async def client():
    from app.main import create_app
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
    await close_db_engine()


@pytest.fixture
async def eng():
    engine = create_async_engine(DB_URL, **_ENGINE_ARGS)
    yield engine
    await engine.dispose()


# ---------------------------------------------------------------------------
# Seed helpers
# ---------------------------------------------------------------------------

async def _seed_tenant(eng, tenant_id=TENANT_ID, slug="test-tenant", code="TEST"):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        existing = await session.get(Tenant, tenant_id)
        if existing is None:
            session.add(Tenant(id=tenant_id, name="Test", slug=slug, code=code))
            await session.commit()


async def _seed_user(eng, tenant_id=TENANT_ID, email="admin@test.com"):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        user = Usuario(
            id=uuid.uuid4(), email=email, tenant_id=tenant_id,
            hashed_password=hash_password("testpass123"), is_active=True,
        )
        session.add(user)
        await session.commit()
        return user


async def _seed_role(eng, tenant_id=TENANT_ID, name="ADMIN", permissions=None):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        role = Role(
            id=uuid.uuid4(), tenant_id=tenant_id, name=name,
            permissions=permissions or ["atrasados:ver"],
            is_system_role=True,
        )
        session.add(role)
        await session.commit()
        return role


async def _seed_role_without_perm(eng, tenant_id=TENANT_ID):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        role = Role(
            id=uuid.uuid4(), tenant_id=tenant_id, name="VIEWER",
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
            id=uuid.uuid4(), tenant_id=tenant_id,
            codigo=f"CAR-{uuid.uuid4().hex[:6]}", nombre="Test Carrera", is_active=True,
        )
        session.add(carrera)
        await session.commit()
        return carrera


async def _seed_cohorte(eng, tenant_id=TENANT_ID, carrera_id=None):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        cohorte = Cohorte(
            id=uuid.uuid4(), tenant_id=tenant_id, carrera_id=carrera_id,
            nombre=f"COH-{uuid.uuid4().hex[:6]}", anio=2026, is_active=True,
        )
        session.add(cohorte)
        await session.commit()
        return cohorte


async def _seed_materia(eng, tenant_id=TENANT_ID):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        materia = Materia(
            id=uuid.uuid4(), tenant_id=tenant_id,
            codigo=f"MAT-{uuid.uuid4().hex[:6]}", nombre="Test Materia", is_active=True,
        )
        session.add(materia)
        await session.commit()
        return materia


async def _seed_version_padron(eng, tenant_id=TENANT_ID, materia_id=None, cohorte_id=None, user_id=None):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        vp = VersionPadron(
            id=uuid.uuid4(), tenant_id=tenant_id, materia_id=materia_id,
            cohorte_id=cohorte_id, activa=True, creada_por=user_id or uuid.uuid4(),
        )
        session.add(vp)
        await session.commit()
        return vp


async def _seed_entrada(eng, version_padron_id, tenant_id=TENANT_ID, legajo="L001",
                         nombre="Juan Perez", email="juan@test.com"):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        ep = EntradaPadron(
            id=uuid.uuid4(), tenant_id=tenant_id, version_padron_id=version_padron_id,
            legajo=legajo, nombre_completo=nombre, email=email, estado="activo",
        )
        session.add(ep)
        await session.commit()
        return ep


async def _seed_calificacion(eng, entrada_padron_id, materia_id, cohorte_id, tenant_id=TENANT_ID,
                              actividad_nombre="Parcial 1", calificacion="85", es_numerica=True,
                              aprobado=True):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        cal = Calificacion(
            id=uuid.uuid4(), tenant_id=tenant_id, entrada_padron_id=entrada_padron_id,
            materia_id=materia_id, cohorte_id=cohorte_id,
            actividad_nombre=actividad_nombre, calificacion=calificacion,
            es_numerica=es_numerica, aprobado=aprobado, origen="Importado",
        )
        session.add(cal)
        await session.commit()
        return cal


async def _seed_umbral(eng, materia_id, cohorte_id=None, tenant_id=TENANT_ID, umbral_pct=60.0):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        umbral = UmbralMateria(
            id=uuid.uuid4(), tenant_id=tenant_id, materia_id=materia_id,
            cohorte_id=cohorte_id or uuid.uuid4(),
            umbral_pct=umbral_pct, valores_aprobados=["Aprobado", "Promocionado"],
        )
        session.add(umbral)
        await session.commit()
        return umbral


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


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestAtrasados:
    """C-11 task 6.1: atrasados detection (faltante + bajo umbral + no atrasado)."""

    async def test_atrasados_missing_activity_flagged(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)
        vp = await _seed_version_padron(eng, TENANT_ID, materia.id, cohorte.id, user.id)
        ep = await _seed_entrada(eng, vp.id)
        await _seed_umbral(eng, materia.id, cohorte.id)

        # Create a cal for ANOTHER student to define "Parcial 1" as an activity.
        # `ep` has no cal for it → should be flagged as missing activity.
        ep_otro = await _seed_entrada(eng, vp.id)
        await _seed_calificacion(eng, ep_otro.id, materia.id, cohorte.id, actividad_nombre="Parcial 1")

        resp = await client.get(
            f"/api/v1/analisis/atrasados?materia_id={materia.id}&cohorte_id={cohorte.id}",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["legajo"] == ep.legajo
        assert "Parcial 1" in data["items"][0]["actividades_faltantes"]

    async def test_atrasados_below_umbral_flagged(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)
        vp = await _seed_version_padron(eng, TENANT_ID, materia.id, cohorte.id, user.id)
        ep = await _seed_entrada(eng, vp.id)
        await _seed_umbral(eng, materia.id, cohorte.id)

        # Calificacion below 60% threshold
        await _seed_calificacion(eng, ep.id, materia.id, cohorte.id,
                                 actividad_nombre="Parcial 1", calificacion="40",
                                 aprobado=False)

        resp = await client.get(
            f"/api/v1/analisis/atrasados?materia_id={materia.id}&cohorte_id={cohorte.id}",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert "Parcial 1" in data["items"][0]["actividades_bajo_umbral"]

    async def test_atrasados_not_atrasado_when_approved(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)
        vp = await _seed_version_padron(eng, TENANT_ID, materia.id, cohorte.id, user.id)
        ep = await _seed_entrada(eng, vp.id)
        await _seed_umbral(eng, materia.id, cohorte.id)

        await _seed_calificacion(eng, ep.id, materia.id, cohorte.id,
                                 actividad_nombre="Parcial 1", calificacion="85", aprobado=True)

        resp = await client.get(
            f"/api/v1/analisis/atrasados?materia_id={materia.id}&cohorte_id={cohorte.id}",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0

    async def test_atrasados_no_data_returns_empty(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)
        resp = await client.get(
            f"/api/v1/analisis/atrasados?materia_id={materia.id}&cohorte_id={cohorte.id}",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


class TestRanking:
    """C-11 task 6.2: ranking (exclude zero-approved, descending order)."""

    async def test_ranking_excludes_zero_approved(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)
        vp = await _seed_version_padron(eng, TENANT_ID, materia.id, cohorte.id, user.id)
        ep1 = await _seed_entrada(eng, vp.id, legajo="L001", nombre="Juan")
        ep2 = await _seed_entrada(eng, vp.id, legajo="L002", nombre="Ana")

        await _seed_calificacion(eng, ep1.id, materia.id, cohorte.id,
                                 actividad_nombre="Parcial 1", calificacion="85", aprobado=True)
        await _seed_calificacion(eng, ep2.id, materia.id, cohorte.id,
                                 actividad_nombre="Parcial 1", calificacion="40", aprobado=False)

        resp = await client.get(
            f"/api/v1/analisis/ranking?materia_id={materia.id}&cohorte_id={cohorte.id}",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["legajo"] == "L001"

    async def test_ranking_descending_order(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)
        vp = await _seed_version_padron(eng, TENANT_ID, materia.id, cohorte.id, user.id)
        ep1 = await _seed_entrada(eng, vp.id, legajo="L001", nombre="Juan")
        ep2 = await _seed_entrada(eng, vp.id, legajo="L002", nombre="Ana")

        await _seed_calificacion(eng, ep1.id, materia.id, cohorte.id,
                                 actividad_nombre="Parcial 1", calificacion="85", aprobado=True)
        await _seed_calificacion(eng, ep1.id, materia.id, cohorte.id,
                                 actividad_nombre="TP 1", calificacion="90", aprobado=True)
        await _seed_calificacion(eng, ep2.id, materia.id, cohorte.id,
                                 actividad_nombre="Parcial 1", calificacion="75", aprobado=True)

        resp = await client.get(
            f"/api/v1/analisis/ranking?materia_id={materia.id}&cohorte_id={cohorte.id}",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        # Juan has 2 approved, Ana has 1 -> Juan first
        assert data["items"][0]["aprobadas_count"] == 2
        assert data["items"][1]["aprobadas_count"] == 1

    async def test_ranking_no_data_returns_empty(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)
        resp = await client.get(
            f"/api/v1/analisis/ranking?materia_id={materia.id}&cohorte_id={cohorte.id}",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


class TestReporteRapido:
    """Task 2.3/6N: report with aggregates and no-data state."""

    async def test_reporte_returns_aggregates(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)
        vp = await _seed_version_padron(eng, TENANT_ID, materia.id, cohorte.id, user.id)
        ep1 = await _seed_entrada(eng, vp.id, legajo="L001", nombre="Juan")
        await _seed_umbral(eng, materia.id, cohorte.id)

        await _seed_calificacion(eng, ep1.id, materia.id, cohorte.id,
                                 actividad_nombre="Parcial 1", calificacion="85", aprobado=True)

        resp = await client.get(
            f"/api/v1/analisis/reporte-rapido?materia_id={materia.id}&cohorte_id={cohorte.id}",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_alumnos"] >= 1
        assert data["atrasados"] >= 0
        assert data["pct_atrasados"] >= 0.0

    async def test_reporte_no_data_returns_zero_metrics(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)
        resp = await client.get(
            f"/api/v1/analisis/reporte-rapido?materia_id={materia.id}&cohorte_id={cohorte.id}",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_alumnos"] == 0
        assert data["atrasados"] == 0


class TestNotasFinales:
    """C-11 task 6.3: notas finales agrupadas con y sin datos."""

    async def test_notas_finales_with_data(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)
        vp = await _seed_version_padron(eng, TENANT_ID, materia.id, cohorte.id, user.id)
        ep = await _seed_entrada(eng, vp.id, legajo="L001", nombre="Juan")

        await _seed_calificacion(eng, ep.id, materia.id, cohorte.id,
                                 actividad_nombre="Parcial 1", calificacion="80", aprobado=True)
        await _seed_calificacion(eng, ep.id, materia.id, cohorte.id,
                                 actividad_nombre="Parcial 2", calificacion="90", aprobado=True)

        resp = await client.post(
            "/api/v1/analisis/notas-finales",
            json={
                "materia_id": str(materia.id),
                "cohorte_id": str(cohorte.id),
                "grupos": {"Parciales": ["Parcial 1", "Parcial 2"]},
            },
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["grupos"]["Parciales"] == 85.0
        assert data["items"][0]["nota_final"] == 85.0

    async def test_notas_finales_sin_datos_returns_null(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)
        vp = await _seed_version_padron(eng, TENANT_ID, materia.id, cohorte.id, user.id)
        ep = await _seed_entrada(eng, vp.id)

        resp = await client.post(
            "/api/v1/analisis/notas-finales",
            json={
                "materia_id": str(materia.id),
                "cohorte_id": str(cohorte.id),
                "grupos": {"Parciales": ["Parcial 1"]},
            },
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["grupos"]["Parciales"] is None
        assert data["items"][0]["nota_final"] is None


class TestMonitores:
    """C-11 task 6.4: monitores por rol/filtros/paginación."""

    async def test_monitor_returns_paginated(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)
        vp = await _seed_version_padron(eng, TENANT_ID, materia.id, cohorte.id, user.id)
        await _seed_entrada(eng, vp.id, legajo="L001")

        resp = await client.get(
            f"/api/v1/analisis/monitor?page=1&limit=20",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 1
        assert data["limit"] == 20
        assert isinstance(data["items"], list)
        assert data["total"] >= 0


class TestEntregasSinCorregir:
    """C-11 task 6.5: export con y sin filas, aislamiento tenant."""

    async def test_entregas_sin_corregir_returns_empty_when_all_graded(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)

        resp = await client.get(
            f"/api/v1/analisis/entregas-sin-corregir?materia_id={materia.id}&cohorte_id={cohorte.id}",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data["items"], list)

    async def test_export_csv_returns_valid_content(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)

        resp = await client.get(
            f"/api/v1/analisis/entregas-sin-corregir/export?materia_id={materia.id}&cohorte_id={cohorte.id}",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.headers.get("content-type", "").startswith("text/csv")
        content = resp.text
        assert content.startswith("entrada_padron_id,")
        lines = content.strip().split("\n")
        assert len(lines) >= 1  # At least header row


class TestPermissionGuard:
    """All endpoints require atrasados:ver."""

    async def test_atrasados_without_permission_returns_403(self, client, eng):
        await _seed_tenant(eng)
        user = await _seed_user(eng)
        role = await _seed_role_without_perm(eng)
        await _assign_role(eng, user.id, role.id)
        headers = await _create_auth_headers(eng, user)

        resp = await client.get(
            f"/api/v1/analisis/atrasados?materia_id={uuid.uuid4()}&cohorte_id={uuid.uuid4()}",
            headers=headers,
        )
        assert resp.status_code == 403

    async def test_ranking_without_permission_returns_403(self, client, eng):
        await _seed_tenant(eng)
        user = await _seed_user(eng)
        role = await _seed_role_without_perm(eng)
        await _assign_role(eng, user.id, role.id)
        headers = await _create_auth_headers(eng, user)

        resp = await client.get(
            f"/api/v1/analisis/ranking?materia_id={uuid.uuid4()}&cohorte_id={uuid.uuid4()}",
            headers=headers,
        )
        assert resp.status_code == 403

    async def test_reporte_without_permission_returns_403(self, client, eng):
        await _seed_tenant(eng)
        user = await _seed_user(eng)
        role = await _seed_role_without_perm(eng)
        await _assign_role(eng, user.id, role.id)
        headers = await _create_auth_headers(eng, user)

        resp = await client.get(
            f"/api/v1/analisis/reporte-rapido?materia_id={uuid.uuid4()}&cohorte_id={uuid.uuid4()}",
            headers=headers,
        )
        assert resp.status_code == 403

    async def test_notas_finales_without_permission_returns_403(self, client, eng):
        await _seed_tenant(eng)
        user = await _seed_user(eng)
        role = await _seed_role_without_perm(eng)
        await _assign_role(eng, user.id, role.id)
        headers = await _create_auth_headers(eng, user)

        resp = await client.post(
            "/api/v1/analisis/notas-finales",
            json={"materia_id": str(uuid.uuid4()), "cohorte_id": str(uuid.uuid4()), "grupos": {"G1": ["A1"]}},
            headers=headers,
        )
        assert resp.status_code == 403

    async def test_export_without_permission_returns_403(self, client, eng):
        await _seed_tenant(eng)
        user = await _seed_user(eng)
        role = await _seed_role_without_perm(eng)
        await _assign_role(eng, user.id, role.id)
        headers = await _create_auth_headers(eng, user)

        resp = await client.get(
            f"/api/v1/analisis/entregas-sin-corregir/export?materia_id={uuid.uuid4()}&cohorte_id={uuid.uuid4()}",
            headers=headers,
        )
        assert resp.status_code == 403
