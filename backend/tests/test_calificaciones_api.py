"""Integration tests for calificaciones import, umbral management and permission guards."""
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
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.models.role import Role
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.models.usuario_role import UsuarioRole
from app.models.version_padron import VersionPadron
from app.services.calificacion_service import _compute_aprobado

pytestmark = pytest.mark.asyncio

_db_host = os.environ.get('POSTGRES_HOST', 'localhost')
DB_URL = f"postgresql+asyncpg://active_trace:active_trace@{_db_host}:5432/active_trace_test"
TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
TENANT2_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


class MockUmbral:
    def __init__(self, umbral_pct=60.0, valores_aprobados=None):
        self.umbral_pct = umbral_pct
        self.valores_aprobados = valores_aprobados or ["Aprobado", "Promocionado"]


class TestComputeAprobado:
    async def test_numeric_above_threshold_returns_true(self):
        umbral = MockUmbral(umbral_pct=60.0)
        assert await _compute_aprobado("85", True, umbral) is True

    async def test_numeric_below_threshold_returns_false(self):
        umbral = MockUmbral(umbral_pct=60.0)
        assert await _compute_aprobado("40", True, umbral) is False

    async def test_textual_aprobado_in_set_returns_true(self):
        umbral = MockUmbral(valores_aprobados=["Aprobado", "Promocionado"])
        assert await _compute_aprobado("Aprobado", False, umbral) is True

    async def test_textual_desaprobado_not_in_set_returns_false(self):
        umbral = MockUmbral(valores_aprobados=["Aprobado", "Promocionado"])
        assert await _compute_aprobado("Desaprobado", False, umbral) is False

    async def test_textual_empty_string_not_in_set_returns_false(self):
        umbral = MockUmbral(valores_aprobados=["Aprobado", "Promocionado"])
        assert await _compute_aprobado("", False, umbral) is False

    async def test_numeric_invalid_string_returns_false(self):
        umbral = MockUmbral(umbral_pct=60.0)
        assert await _compute_aprobado("N/A", True, umbral) is False

    async def test_numeric_exact_threshold_returns_true(self):
        umbral = MockUmbral(umbral_pct=60.0)
        assert await _compute_aprobado("60", True, umbral) is True

    async def test_numeric_decimal_above_threshold_returns_true(self):
        umbral = MockUmbral(umbral_pct=60.0)
        assert await _compute_aprobado("75.5", True, umbral) is True


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
            permissions=permissions or ["calificaciones:importar", "calificaciones:configurar-umbral"],
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
            codigo=f"TCAL-{uuid.uuid4().hex[:6]}",
            nombre="Tecnicatura Calificaciones",
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
            nombre=f"CAL-{uuid.uuid4().hex[:6]}",
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
            codigo=f"CAL-{uuid.uuid4().hex[:6]}",
            nombre="Materia Calificaciones",
            is_active=True,
        )
        session.add(materia)
        await session.commit()
        return materia


async def _seed_entrada_padron(
    eng,
    tenant_id=TENANT_ID,
    user_id=None,
    legajo="1234",
    nombre="Test User",
    materia_id=None,
    cohorte_id=None,
):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        version = VersionPadron(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            materia_id=materia_id or uuid.uuid4(),
            cohorte_id=cohorte_id or uuid.uuid4(),
            activa=True,
            creada_por=user_id or uuid.uuid4(),
        )
        session.add(version)
        await session.flush()
        entrada = EntradaPadron(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            version_padron_id=version.id,
            legajo=legajo,
            nombre_completo=nombre,
            email=f"{legajo}@test.com",
        )
        session.add(entrada)
        await session.commit()
        return entrada


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


class TestImportPreview:
    async def test_preview_detects_columns(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)
        ep1 = await _seed_entrada_padron(
            eng, TENANT_ID, user.id, "1234", "Juan Perez", materia.id, cohorte.id,
        )
        ep2 = await _seed_entrada_padron(
            eng, TENANT_ID, user.id, "5678", "Ana Gomez", materia.id, cohorte.id,
        )

        content = f"entrada_padron_id,legajo,nombre_completo,Parcial 1,Trabajo Practico\n{ep1.id},{ep1.legajo},{ep1.nombre_completo},85,Aprobado\n{ep2.id},{ep2.legajo},{ep2.nombre_completo},40,Desaprobado"
        files = {"file": ("calificaciones.csv", io.BytesIO(content.encode("utf-8")), "text/csv")}
        resp = await client.post(
            f"/api/v1/calificaciones/import/preview?materia_id={materia.id}&cohorte_id={cohorte.id}",
            files=files,
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["columns"]) == 2
        col_map = {c["actividad_nombre"]: c for c in data["columns"]}
        assert col_map["Parcial 1"]["es_numerica"] is True
        assert col_map["Trabajo Practico"]["es_numerica"] is False
        assert len(data["rows"]) == 2
        assert data["preview_hash"] is not None

    async def test_preview_no_activity_columns_returns_400(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)

        content = "entrada_padron_id,legajo,nombre_completo\n{},1234,Juan Perez".format(uuid.uuid4())
        files = {"file": ("bad.csv", io.BytesIO(content.encode("utf-8")), "text/csv")}
        resp = await client.post(
            f"/api/v1/calificaciones/import/preview?materia_id={materia.id}&cohorte_id={cohorte.id}",
            files=files,
            headers=headers,
        )
        assert resp.status_code == 400

    async def test_preview_mixed_values_marks_column_as_textual(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)
        ep1 = await _seed_entrada_padron(
            eng, TENANT_ID, user.id, "1234", "Juan Perez", materia.id, cohorte.id,
        )
        ep2 = await _seed_entrada_padron(
            eng, TENANT_ID, user.id, "5678", "Ana Gomez", materia.id, cohorte.id,
        )

        content = (
            "entrada_padron_id,legajo,nombre_completo,Parcial 1\n"
            f"{ep1.id},{ep1.legajo},{ep1.nombre_completo},85\n"
            f"{ep2.id},{ep2.legajo},{ep2.nombre_completo},N/A"
        )
        files = {"file": ("calificaciones.csv", io.BytesIO(content.encode("utf-8")), "text/csv")}
        resp = await client.post(
            f"/api/v1/calificaciones/import/preview?materia_id={materia.id}&cohorte_id={cohorte.id}",
            files=files,
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["columns"][0]["actividad_nombre"] == "Parcial 1"
        assert data["columns"][0]["es_numerica"] is False


class TestImportConfirm:
    async def test_confirm_import_creates_calificaciones(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)
        ep1 = await _seed_entrada_padron(
            eng, TENANT_ID, user.id, "1234", "Juan Perez", materia.id, cohorte.id,
        )
        ep2 = await _seed_entrada_padron(
            eng, TENANT_ID, user.id, "5678", "Ana Gomez", materia.id, cohorte.id,
        )

        content = f"entrada_padron_id,legajo,nombre_completo,Parcial 1,Trabajo Practico\n{ep1.id},{ep1.legajo},{ep1.nombre_completo},85,Aprobado\n{ep2.id},{ep2.legajo},{ep2.nombre_completo},40,Desaprobado"
        files = {"file": ("cal.csv", io.BytesIO(content.encode("utf-8")), "text/csv")}
        preview_resp = await client.post(
            f"/api/v1/calificaciones/import/preview?materia_id={materia.id}&cohorte_id={cohorte.id}",
            files=files,
            headers=headers,
        )
        assert preview_resp.status_code == 200
        preview = preview_resp.json()

        confirm_resp = await client.post(
            "/api/v1/calificaciones/import/confirm",
            json={
                "materia_id": str(materia.id),
                "cohorte_id": str(cohorte.id),
                "selected_activities": ["Parcial 1"],
                "preview_hash": preview["preview_hash"],
                "rows": preview["rows"],
            },
            headers=headers,
        )
        if confirm_resp.status_code != 201:
            print(f"CONFIRM ERROR: {confirm_resp.status_code} {confirm_resp.text}")
        assert confirm_resp.status_code == 201
        data = confirm_resp.json()
        assert data["total_creados"] == 2

    async def test_confirm_import_rejects_changed_preview_hash(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)
        ep1 = await _seed_entrada_padron(
            eng, TENANT_ID, user.id, "1234", "Juan Perez", materia.id, cohorte.id,
        )

        content = (
            "entrada_padron_id,legajo,nombre_completo,Parcial 1\n"
            f"{ep1.id},{ep1.legajo},{ep1.nombre_completo},85"
        )
        files = {"file": ("cal.csv", io.BytesIO(content.encode("utf-8")), "text/csv")}
        preview_resp = await client.post(
            f"/api/v1/calificaciones/import/preview?materia_id={materia.id}&cohorte_id={cohorte.id}",
            files=files,
            headers=headers,
        )
        assert preview_resp.status_code == 200
        preview = preview_resp.json()

        confirm_resp = await client.post(
            "/api/v1/calificaciones/import/confirm",
            json={
                "materia_id": str(materia.id),
                "cohorte_id": str(cohorte.id),
                "selected_activities": ["Parcial 1"],
                "preview_hash": f"{preview['preview_hash']}BAD",
                "rows": preview["rows"],
            },
            headers=headers,
        )
        assert confirm_resp.status_code == 400


class TestUmbralMateria:
    async def test_get_umbral_returns_default_when_not_set(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)

        resp = await client.get(
            f"/api/v1/umbrales?materia_id={materia.id}",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["umbral_pct"] == 60.0
        assert data["valores_aprobados"] == ["Aprobado", "Promocionado"]

    async def test_umbral_isolation_between_materias(self, client, eng):
        user, materia_a, cohorte, _ = await _build_test_data(eng, TENANT_ID, "test-tenant", "TEST")
        materia_b = await _seed_materia(eng, TENANT_ID)
        headers = await _create_auth_headers(eng, user)

        upsert_resp = await client.put(
            f"/api/v1/umbrales/materia/{materia_a.id}",
            json={"umbral_pct": 80.0, "valores_aprobados": ["Aprobado"]},
            headers=headers,
        )
        assert upsert_resp.status_code == 200

        resp_a = await client.get(
            f"/api/v1/umbrales?materia_id={materia_a.id}",
            headers=headers,
        )
        assert resp_a.status_code == 200
        assert resp_a.json()["umbral_pct"] == 80.0

        resp_b = await client.get(
            f"/api/v1/umbrales?materia_id={materia_b.id}",
            headers=headers,
        )
        assert resp_b.status_code == 200
        assert resp_b.json()["umbral_pct"] == 60.0


class TestPermissionGuard:
    async def test_import_preview_without_permission_returns_403(self, client, eng):
        await _seed_tenant(eng)
        user = await _seed_user(eng)
        await _seed_role_no_permission(eng)
        headers = await _create_auth_headers(eng, user)

        content = "entrada_padron_id,legajo,nombre_completo,Parcial 1\n1,1234,Juan Perez,85"
        files = {"file": ("d.csv", io.BytesIO(content.encode("utf-8")), "text/csv")}
        resp = await client.post(
            f"/api/v1/calificaciones/import/preview?materia_id={uuid.uuid4()}&cohorte_id={uuid.uuid4()}",
            files=files,
            headers=headers,
        )
        assert resp.status_code == 403

    async def test_umbral_update_without_permission_returns_403(self, client, eng):
        await _seed_tenant(eng)
        user = await _seed_user(eng)
        await _seed_role_no_permission(eng)
        headers = await _create_auth_headers(eng, user)

        resp = await client.put(
            f"/api/v1/umbrales/materia/{uuid.uuid4()}",
            json={"umbral_pct": 70.0},
            headers=headers,
        )
        assert resp.status_code == 403
