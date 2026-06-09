"""Tests for C-18 liquidaciones y honorarios — 12 test suites (8.1–8.12)."""

import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base, close_db_engine
from app.core.security import create_access_token, hash_password
from app.models.asignacion import Asignacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.factura import Factura
from app.models.liquidacion import Liquidacion
from app.models.materia import Materia
from app.models.materia_grupo_plus import MateriaGrupoPlus
from app.models.role import Role
from app.models.salario_base import SalarioBase
from app.models.salario_plus import SalarioPlus
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.models.usuario_role import UsuarioRole
from app.repositories.materia_grupo_plus_repository import MateriaGrupoPlusRepository
from app.repositories.salario_base_repository import SalarioBaseRepository
from app.repositories.salario_plus_repository import SalarioPlusRepository

pytestmark = pytest.mark.asyncio

DB_URL = "postgresql+asyncpg://active_trace:active_trace@localhost:5432/active_trace_test"
TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
TENANT2_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")

_FINANZAS_PERMISSIONS = [
    "liquidaciones:calcular",
    "liquidaciones:ver",
    "liquidaciones:cerrar",
    "liquidaciones:exportar",
    "liquidaciones:configurar-salarios",
    "liquidaciones:gestionar-facturas",
]


# ── Helpers ──────────────────────────────────────────────────────────

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


async def _make_engine():
    return create_async_engine(DB_URL, echo=False)


def _factory(eng):
    return async_sessionmaker(eng, expire_on_commit=False)


async def _seed_tenant(eng, tenant_id=TENANT_ID, slug="test-tenant", code="TEST"):
    factory = _factory(eng)
    async with factory() as session:
        tenant = Tenant(id=tenant_id, name="Test", slug=slug, code=code)
        session.add(tenant)
        await session.commit()


async def _seed_user(
    eng, tenant_id=TENANT_ID, email=None, facturador=False,
):
    factory = _factory(eng)
    async with factory() as session:
        user = Usuario(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            email=email or f"user-{uuid.uuid4().hex[:8]}@test.com",
            hashed_password=hash_password("testpass123"),
            is_active=True,
            facturador=facturador,
        )
        session.add(user)
        await session.commit()
        return user


async def _seed_role(
    eng, tenant_id=TENANT_ID, name="FINANZAS", permissions=None, system=True,
):
    factory = _factory(eng)
    async with factory() as session:
        role = Role(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name=name,
            permissions=permissions or _FINANZAS_PERMISSIONS,
            is_system_role=system,
        )
        session.add(role)
        await session.commit()
        return role


async def _assign_role(eng, user_id, role_id, tenant_id=TENANT_ID):
    factory = _factory(eng)
    async with factory() as session:
        session.add(UsuarioRole(usuario_id=user_id, role_id=role_id, tenant_id=tenant_id))
        await session.commit()


async def _seed_carrera(eng, tenant_id=TENANT_ID, codigo="CARR-001", nombre="Test Carrera"):
    factory = _factory(eng)
    async with factory() as session:
        carrera = Carrera(
            id=uuid.uuid4(), tenant_id=tenant_id,
            codigo=codigo, nombre=nombre, is_active=True,
        )
        session.add(carrera)
        await session.commit()
        return carrera


async def _seed_cohorte(eng, tenant_id, carrera_id, nombre="2026", anio=2026):
    factory = _factory(eng)
    async with factory() as session:
        cohorte = Cohorte(
            id=uuid.uuid4(), tenant_id=tenant_id,
            carrera_id=carrera_id, nombre=nombre, anio=anio, is_active=True,
        )
        session.add(cohorte)
        await session.commit()
        return cohorte


async def _seed_materia(eng, tenant_id, codigo="MAT-001", nombre="Materia Test"):
    factory = _factory(eng)
    async with factory() as session:
        materia = Materia(
            id=uuid.uuid4(), tenant_id=tenant_id,
            codigo=codigo, nombre=nombre,
        )
        session.add(materia)
        await session.commit()
        return materia


async def _seed_asignacion(
    eng, tenant_id, usuario_id, materia_id, cohorte_id, rol="PROFESOR",
):
    factory = _factory(eng)
    async with factory() as session:
        asignacion = Asignacion(
            id=uuid.uuid4(), tenant_id=tenant_id,
            usuario_id=usuario_id, rol=rol,
            materia_id=materia_id, cohorte_id=cohorte_id,
            fecha_inicio=date(2026, 1, 1), is_active=True,
        )
        session.add(asignacion)
        await session.commit()
        return asignacion


async def _seed_salario_base(eng, tenant_id, rol="PROFESOR", monto=1000):
    factory = _factory(eng)
    async with factory() as session:
        sb = SalarioBase(
            id=uuid.uuid4(), tenant_id=tenant_id,
            rol=rol, monto=monto,
            desde=date(2026, 1, 1), hasta=date(2026, 12, 31),
        )
        session.add(sb)
        await session.commit()
        return sb


async def _seed_salario_plus(
    eng, tenant_id, grupo="GRUPO_A", rol="PROFESOR",
    monto=200, tope_acumulacion=None,
):
    factory = _factory(eng)
    async with factory() as session:
        sp = SalarioPlus(
            id=uuid.uuid4(), tenant_id=tenant_id,
            grupo=grupo, rol=rol, descripcion="Plus test",
            monto=monto, tope_acumulacion=tope_acumulacion,
            desde=date(2026, 1, 1), hasta=date(2026, 12, 31),
        )
        session.add(sp)
        await session.commit()
        return sp


async def _seed_materia_grupo(eng, tenant_id, materia_id, grupo="GRUPO_A"):
    factory = _factory(eng)
    async with factory() as session:
        mgp = MateriaGrupoPlus(
            id=uuid.uuid4(), tenant_id=tenant_id,
            materia_id=materia_id, grupo=grupo,
            desde=date(2026, 1, 1), hasta=date(2026, 12, 31),
        )
        session.add(mgp)
        await session.commit()
        return mgp


async def _make_app():
    from app.main import create_app
    app = create_app()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


async def _seed_full_calcular_scenario(
    eng, tenant_id=TENANT_ID, docente_rol="PROFESOR", facturador=False,
):
    """Seed complete data for a calcular test. Returns dict with all IDs."""
    carrera = await _seed_carrera(eng, tenant_id)
    cohorte = await _seed_cohorte(eng, tenant_id, carrera.id)
    docente = await _seed_user(eng, tenant_id, facturador=facturador)
    mat1 = await _seed_materia(eng, tenant_id, "MAT-101", "Matemáticas")
    mat2 = await _seed_materia(eng, tenant_id, "MAT-102", "Física")
    await _seed_asignacion(eng, tenant_id, docente.id, mat1.id, cohorte.id, docente_rol)
    await _seed_asignacion(eng, tenant_id, docente.id, mat2.id, cohorte.id, docente_rol)
    await _seed_salario_base(eng, tenant_id, docente_rol, 1000)
    await _seed_salario_plus(eng, tenant_id, "GRUPO_A", docente_rol, 200, None)
    await _seed_materia_grupo(eng, tenant_id, mat1.id, "GRUPO_A")
    await _seed_materia_grupo(eng, tenant_id, mat2.id, "GRUPO_A")
    return {
        "cohorte_id": cohorte.id,
        "docente_id": docente.id,
        "mat1": mat1,
        "mat2": mat2,
    }


# ═══════════════════════════════════════════════════════════════════════
# 8.1 — SalarioBaseRepository.find_vigente por periodo
# ═══════════════════════════════════════════════════════════════════════

class TestSalarioBaseFindVigente:
    """Repository-level: SalarioBaseRepository.find_vigente within/beyond period."""

    async def test_encuentra_vigente_dentro_del_periodo(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            factory = _factory(eng)
            async with factory() as session:
                repo = SalarioBaseRepository(session, TENANT_ID)
                sb = await repo.create(
                    tenant_id=TENANT_ID, rol="PROFESOR", monto=1000,
                    desde=date(2026, 1, 1), hasta=date(2026, 6, 30),
                )
                await session.flush()

                result = await repo.find_vigente("PROFESOR", date(2026, 3, 15))
                assert result is not None
                assert result.id == sb.id
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_no_encuentra_fuera_del_periodo(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            factory = _factory(eng)
            async with factory() as session:
                repo = SalarioBaseRepository(session, TENANT_ID)
                await repo.create(
                    tenant_id=TENANT_ID, rol="PROFESOR", monto=1000,
                    desde=date(2026, 1, 1), hasta=date(2026, 6, 30),
                )
                await session.flush()

                result = await repo.find_vigente("PROFESOR", date(2026, 8, 1))
                assert result is None
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_no_encuentra_para_otro_rol(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            factory = _factory(eng)
            async with factory() as session:
                repo = SalarioBaseRepository(session, TENANT_ID)
                await repo.create(
                    tenant_id=TENANT_ID, rol="PROFESOR", monto=1000,
                    desde=date(2026, 1, 1), hasta=date(2026, 12, 31),
                )
                await session.flush()

                result = await repo.find_vigente("TUTOR", date(2026, 3, 15))
                assert result is None
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_encuentra_con_hasta_nulo(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            factory = _factory(eng)
            async with factory() as session:
                repo = SalarioBaseRepository(session, TENANT_ID)
                sb = await repo.create(
                    tenant_id=TENANT_ID, rol="PROFESOR", monto=1000,
                    desde=date(2026, 1, 1), hasta=None,
                )
                await session.flush()

                result = await repo.find_vigente("PROFESOR", date(2027, 6, 1))
                assert result is not None
                assert result.id == sb.id
        finally:
            await _teardown_db()
            await eng.dispose()


# ═══════════════════════════════════════════════════════════════════════
# 8.2 — SalarioPlus con tope_acumulacion NULL y numerico
# ═══════════════════════════════════════════════════════════════════════

class TestTopeAcumulacion:
    """Plus with tope_acumulacion = NULL counts all; numeric caps efectivas."""

    async def test_sin_tope_cuenta_todas_las_materias(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["FINANZAS"]},
            )
            data = await _seed_full_calcular_scenario(eng, TENANT_ID, "PROFESOR", False)

            async with await _make_app() as client:
                resp = await client.post(
                    "/api/liquidaciones/calcular",
                    json={"cohorte_id": str(data["cohorte_id"]), "periodo": "2026-03"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert resp.status_code == 201
            items = resp.json()["items"]
            assert len(items) == 1
            comisiones = items[0]["comisiones"]
            assert any("2comisiones:2efectivas" in c for c in comisiones)
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_con_tope_capada_en_2(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["FINANZAS"]},
            )
            carrera = await _seed_carrera(eng)
            cohorte = await _seed_cohorte(eng, TENANT_ID, carrera.id)
            docente = await _seed_user(eng)
            mat1 = await _seed_materia(eng, TENANT_ID, "MAT-101", "Matemáticas")
            mat2 = await _seed_materia(eng, TENANT_ID, "MAT-102", "Física")
            mat3 = await _seed_materia(eng, TENANT_ID, "MAT-103", "Química")
            await _seed_asignacion(eng, TENANT_ID, docente.id, mat1.id, cohorte.id)
            await _seed_asignacion(eng, TENANT_ID, docente.id, mat2.id, cohorte.id)
            await _seed_asignacion(eng, TENANT_ID, docente.id, mat3.id, cohorte.id)
            await _seed_salario_base(eng, TENANT_ID, "PROFESOR", 1000)
            await _seed_salario_plus(eng, TENANT_ID, "GRUPO_A", "PROFESOR", 200, 2)
            await _seed_materia_grupo(eng, TENANT_ID, mat1.id, "GRUPO_A")
            await _seed_materia_grupo(eng, TENANT_ID, mat2.id, "GRUPO_A")
            await _seed_materia_grupo(eng, TENANT_ID, mat3.id, "GRUPO_A")

            async with await _make_app() as client:
                resp = await client.post(
                    "/api/liquidaciones/calcular",
                    json={"cohorte_id": str(cohorte.id), "periodo": "2026-03"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert resp.status_code == 201
            items = resp.json()["items"]
            assert len(items) == 1
            comisiones = items[0]["comisiones"]
            assert any("3comisiones:2efectivas" in c for c in comisiones)
        finally:
            await _teardown_db()
            await eng.dispose()


# ═══════════════════════════════════════════════════════════════════════
# 8.3 — Total = base + plus
# ═══════════════════════════════════════════════════════════════════════

class TestTotalBasePlus:
    """Verifica que total = monto_base + sum(plus.monto * N_efectivas)."""

    async def test_total_correcto_con_2_materias_sin_tope(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["FINANZAS"]},
            )
            data = await _seed_full_calcular_scenario(eng, TENANT_ID, "PROFESOR", False)

            async with await _make_app() as client:
                resp = await client.post(
                    "/api/liquidaciones/calcular",
                    json={"cohorte_id": str(data["cohorte_id"]), "periodo": "2026-03"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert resp.status_code == 201
            item = resp.json()["items"][0]
            # base=1000, plus=200 * 2 efectivas = 1400
            assert item["monto_base"] == 1000.0
            assert item["monto_plus"] == 400.0
            assert item["total"] == 1400.0
        finally:
            await _teardown_db()
            await eng.dispose()


# ═══════════════════════════════════════════════════════════════════════
# 8.4 — Liquidacion cerrar (success + double-close 409)
# 8.5 — Inmutabilidad post-cierre
# ═══════════════════════════════════════════════════════════════════════

class TestCierreLiquidacion:
    """Cierre exitoso, doble cierre rechazado e inmutabilidad."""

    async def test_cerrar_exitoso(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["FINANZAS"]},
            )
            data = await _seed_full_calcular_scenario(eng)

            async with await _make_app() as client:
                calc = await client.post(
                    "/api/liquidaciones/calcular",
                    json={"cohorte_id": str(data["cohorte_id"]), "periodo": "2026-03"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert calc.status_code == 201
            liq_id = calc.json()["items"][0]["id"]
            assert calc.json()["items"][0]["estado"] == "Abierta"

            async with await _make_app() as client:
                cerrar = await client.post(
                    f"/api/liquidaciones/{liq_id}/cerrar",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert cerrar.status_code == 200
            assert cerrar.json()["estado"] == "Cerrada"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_doble_cierre_retorna_409(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["FINANZAS"]},
            )
            data = await _seed_full_calcular_scenario(eng)

            async with await _make_app() as client:
                calc = await client.post(
                    "/api/liquidaciones/calcular",
                    json={"cohorte_id": str(data["cohorte_id"]), "periodo": "2026-03"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            liq_id = calc.json()["items"][0]["id"]

            async with await _make_app() as client:
                await client.post(
                    f"/api/liquidaciones/{liq_id}/cerrar",
                    headers={"Authorization": f"Bearer {token}"},
                )
                segundo = await client.post(
                    f"/api/liquidaciones/{liq_id}/cerrar",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert segundo.status_code == 409
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_inmutabilidad_post_cierre_valores_preservados(self):
        """8.5: Despues de cerrar, los valores se preservan."""
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["FINANZAS"]},
            )
            data = await _seed_full_calcular_scenario(eng)

            async with await _make_app() as client:
                calc = await client.post(
                    "/api/liquidaciones/calcular",
                    json={"cohorte_id": str(data["cohorte_id"]), "periodo": "2026-03"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            liq_id = calc.json()["items"][0]["id"]
            expected = calc.json()["items"][0]

            async with await _make_app() as client:
                await client.post(
                    f"/api/liquidaciones/{liq_id}/cerrar",
                    headers={"Authorization": f"Bearer {token}"},
                )
                get = await client.get(
                    f"/api/liquidaciones/{liq_id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert get.status_code == 200
            data = get.json()
            assert data["estado"] == "Cerrada"
            assert data["monto_base"] == expected["monto_base"]
            assert data["monto_plus"] == expected["monto_plus"]
            assert data["total"] == expected["total"]

            async with await _make_app() as client:
                recalcular = await client.post(
                    "/api/liquidaciones/calcular",
                    json={"cohorte_id": str(data["cohorte_id"]), "periodo": "2026-03"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert recalcular.status_code == 409
        finally:
            await _teardown_db()
            await eng.dispose()


# ═══════════════════════════════════════════════════════════════════════
# 8.6 — MateriaGrupoPlusRepository.find_vigente
# ═══════════════════════════════════════════════════════════════════════

class TestMateriaGrupoPlusFindVigente:
    """Materia→grupo mapping vigente by period."""

    async def test_encuentra_vigente_dentro_del_periodo(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            materia = await _seed_materia(eng, TENANT_ID)
            factory = _factory(eng)
            async with factory() as session:
                mgp = MateriaGrupoPlus(
                    id=uuid.uuid4(), tenant_id=TENANT_ID,
                    materia_id=materia.id, grupo="GRUPO_X",
                    desde=date(2026, 1, 1), hasta=date(2026, 6, 30),
                )
                session.add(mgp)
                await session.flush()

                repo = MateriaGrupoPlusRepository(session, TENANT_ID)
                result = await repo.find_vigente(materia.id, date(2026, 3, 15))
                assert result is not None
                assert result.id == mgp.id
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_no_encuentra_fuera_del_periodo(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            materia = await _seed_materia(eng, TENANT_ID)
            factory = _factory(eng)
            async with factory() as session:
                session.add(MateriaGrupoPlus(
                    id=uuid.uuid4(), tenant_id=TENANT_ID,
                    materia_id=materia.id, grupo="GRUPO_X",
                    desde=date(2026, 1, 1), hasta=date(2026, 6, 30),
                ))
                await session.flush()

                repo = MateriaGrupoPlusRepository(session, TENANT_ID)
                result = await repo.find_vigente(materia.id, date(2026, 8, 1))
                assert result is None
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_con_hasta_nulo(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            materia = await _seed_materia(eng, TENANT_ID)
            factory = _factory(eng)
            async with factory() as session:
                mgp = MateriaGrupoPlus(
                    id=uuid.uuid4(), tenant_id=TENANT_ID,
                    materia_id=materia.id, grupo="GRUPO_X",
                    desde=date(2026, 1, 1), hasta=None,
                )
                session.add(mgp)
                await session.flush()

                repo = MateriaGrupoPlusRepository(session, TENANT_ID)
                result = await repo.find_vigente(materia.id, date(2027, 6, 1))
                assert result is not None
        finally:
            await _teardown_db()
            await eng.dispose()


# ═══════════════════════════════════════════════════════════════════════
# 8.7 — Exclusion de facturante (excluido_por_factura = True)
# ═══════════════════════════════════════════════════════════════════════

class TestExclusionFacturante:
    """Docentes con facturador=True deben tener excluido_por_factura=True."""

    async def test_docente_facturante_excluido(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["FINANZAS"]},
            )
            data = await _seed_full_calcular_scenario(eng, TENANT_ID, "PROFESOR", facturador=True)

            async with await _make_app() as client:
                resp = await client.post(
                    "/api/liquidaciones/calcular",
                    json={"cohorte_id": str(data["cohorte_id"]), "periodo": "2026-03"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert resp.status_code == 201
            item = resp.json()["items"][0]
            assert item["excluido_por_factura"] is True
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_docente_no_facturante_no_excluido(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["FINANZAS"]},
            )
            data = await _seed_full_calcular_scenario(eng, TENANT_ID, "PROFESOR", facturador=False)

            async with await _make_app() as client:
                resp = await client.post(
                    "/api/liquidaciones/calcular",
                    json={"cohorte_id": str(data["cohorte_id"]), "periodo": "2026-03"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert resp.status_code == 201
            item = resp.json()["items"][0]
            assert item["excluido_por_factura"] is False
        finally:
            await _teardown_db()
            await eng.dispose()


# ═══════════════════════════════════════════════════════════════════════
# 8.8 — NEXO segmentation (es_nexo = true, summed to total)
# ═══════════════════════════════════════════════════════════════════════

class TestNexoSegmentation:
    """Usuarios con rol NEXO tienen es_nexo = True."""

    async def test_docente_nexo_marca_es_nexo(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["FINANZAS"]},
            )
            data = await _seed_full_calcular_scenario(eng, TENANT_ID, "NEXO", False)

            async with await _make_app() as client:
                resp = await client.post(
                    "/api/liquidaciones/calcular",
                    json={"cohorte_id": str(data["cohorte_id"]), "periodo": "2026-03"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert resp.status_code == 201
            item = resp.json()["items"][0]
            assert item["es_nexo"] is True
        finally:
            await _teardown_db()
            await eng.dispose()


# ═══════════════════════════════════════════════════════════════════════
# 8.9 — Factura CRUD + estado change Pendiente/Abonada
# ═══════════════════════════════════════════════════════════════════════

class TestFacturaCrud:
    """CRUD de facturas y cambio de estado."""

    async def test_crear_y_obtener_factura(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["FINANZAS"]},
            )
            facturante = await _seed_user(eng, facturador=True)

            async with await _make_app() as client:
                resp = await client.post(
                    "/api/facturas",
                    json={
                        "usuario_id": str(facturante.id),
                        "periodo": "2026-03",
                        "detalle": "Honorarios marzo",
                        "referencia_archivo": "factura_marzo.pdf",
                        "tamano_kb": 1024.5,
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert resp.status_code == 201
            data = resp.json()
            assert data["periodo"] == "2026-03"
            assert data["estado"] == "Pendiente"
            assert data["referencia_archivo"] == "factura_marzo.pdf"
            assert data["tamano_kb"] == 1024.5

            async with await _make_app() as client:
                get = await client.get(
                    f"/api/facturas",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert get.status_code == 200
            assert get.json()["total"] == 1
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_cambiar_estado_a_abonada(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["FINANZAS"]},
            )
            facturante = await _seed_user(eng, facturador=True)

            async with await _make_app() as client:
                created = await client.post(
                    "/api/facturas",
                    json={
                        "usuario_id": str(facturante.id),
                        "periodo": "2026-03",
                        "detalle": "Honorarios",
                        "referencia_archivo": "fact.pdf",
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            factura_id = created.json()["id"]

            async with await _make_app() as client:
                patch = await client.patch(
                    f"/api/facturas/{factura_id}/estado",
                    json={"estado": "Abonada"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert patch.status_code == 200
            assert patch.json()["estado"] == "Abonada"
            assert patch.json()["abonada_at"] is not None

            async with await _make_app() as client:
                patch_back = await client.patch(
                    f"/api/facturas/{factura_id}/estado",
                    json={"estado": "Pendiente"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert patch_back.status_code == 200
            assert patch_back.json()["estado"] == "Pendiente"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_rechaza_docente_no_facturante(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["FINANZAS"]},
            )
            no_facturante = await _seed_user(eng, facturador=False)

            async with await _make_app() as client:
                resp = await client.post(
                    "/api/facturas",
                    json={
                        "usuario_id": str(no_facturante.id),
                        "periodo": "2026-03",
                        "detalle": "Test",
                        "referencia_archivo": "test.pdf",
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert resp.status_code == 422
        finally:
            await _teardown_db()
            await eng.dispose()


# ═══════════════════════════════════════════════════════════════════════
# 8.10 — Permisos: FINANZAS puede, otros roles 403
# ═══════════════════════════════════════════════════════════════════════

class TestPermissionGuard:
    """RBAC: FINANZAS pasa, roles sin permiso reciben 403."""

    async def test_finanzas_puede_acceder_a_liquidaciones(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["FINANZAS"]},
            )

            async with await _make_app() as client:
                resp = await client.get(
                    "/api/liquidaciones",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert resp.status_code == 200
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_finanzas_puede_crear_salario_base(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["FINANZAS"]},
            )

            async with await _make_app() as client:
                resp = await client.post(
                    "/api/liquidaciones/salarios-base",
                    json={
                        "rol": "PROFESOR", "monto": 1500,
                        "desde": "2026-01-01", "hasta": "2026-12-31",
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert resp.status_code == 201
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_finanzas_puede_crear_factura(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["FINANZAS"]},
            )
            facturante = await _seed_user(eng, facturador=True)

            async with await _make_app() as client:
                resp = await client.post(
                    "/api/facturas",
                    json={
                        "usuario_id": str(facturante.id),
                        "periodo": "2026-03",
                        "detalle": "Test",
                        "referencia_archivo": "test.pdf",
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert resp.status_code == 201
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_rol_sin_permiso_recibe_403(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            limited = await _seed_role(
                eng, name="LIMITED", permissions=["test:read"], system=False,
            )
            await _assign_role(eng, user.id, limited.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["LIMITED"]},
            )

            async with await _make_app() as client:
                resp = await client.get(
                    "/api/liquidaciones",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert resp.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_sin_autenticacion_recibe_401(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)

            async with await _make_app() as client:
                resp = await client.post(
                    "/api/liquidaciones/salarios-base",
                    json={"rol": "PROFESOR", "monto": 1000, "desde": "2026-01-01"},
                )
            assert resp.status_code == 401
        finally:
            await _teardown_db()
            await eng.dispose()


# ═══════════════════════════════════════════════════════════════════════
# 8.11 — Multi-tenant isolation
# ═══════════════════════════════════════════════════════════════════════

class TestMultiTenantIsolation:
    """Datos en tenant A no son visibles desde tenant B."""

    async def test_liquidaciones_aisladas_por_tenant(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng, TENANT_ID, "tenant-a", "TEN_A")
            await _seed_tenant(eng, TENANT2_ID, "tenant-b", "TEN_B")

            # Seed data only in tenant A
            user_a = await _seed_user(eng, TENANT_ID, "admin@a.com")
            role_a = await _seed_role(eng, TENANT_ID, "FINANZAS_A", _FINANZAS_PERMISSIONS)
            await _assign_role(eng, user_a.id, role_a.id, TENANT_ID)

            carrera_a = await _seed_carrera(eng, TENANT_ID, "CARR-A", "Carrera A")
            cohorte_a = await _seed_cohorte(eng, TENANT_ID, carrera_a.id, "2026-A")
            docente_a = await _seed_user(eng, TENANT_ID, "docente@a.com")
            mat_a = await _seed_materia(eng, TENANT_ID, "MAT-A", "Materia A")
            await _seed_asignacion(eng, TENANT_ID, docente_a.id, mat_a.id, cohorte_a.id)
            await _seed_salario_base(eng, TENANT_ID, "PROFESOR", 1000)
            await _seed_salario_plus(eng, TENANT_ID, "GRUPO_A", "PROFESOR", 200, None)
            await _seed_materia_grupo(eng, TENANT_ID, mat_a.id, "GRUPO_A")

            token_a = create_access_token(
                {"sub": str(user_a.id), "tenant_id": str(TENANT_ID), "roles": ["FINANZAS_A"]},
            )

            # Create liquidacion for tenant A
            async with await _make_app() as client:
                calc_a = await client.post(
                    "/api/liquidaciones/calcular",
                    json={"cohorte_id": str(cohorte_a.id), "periodo": "2026-03"},
                    headers={"Authorization": f"Bearer {token_a}"},
                )
            assert calc_a.status_code == 201
            assert calc_a.json()["total"] == 1

            # User B gets empty list (no liquidacion visible)
            user_b = await _seed_user(eng, TENANT2_ID, "admin@b.com")
            role_b = await _seed_role(eng, TENANT2_ID, "FINANZAS_B", _FINANZAS_PERMISSIONS)
            await _assign_role(eng, user_b.id, role_b.id, TENANT2_ID)
            token_b = create_access_token(
                {"sub": str(user_b.id), "tenant_id": str(TENANT2_ID), "roles": ["FINANZAS_B"]},
            )

            async with await _make_app() as client:
                list_b = await client.get(
                    "/api/liquidaciones",
                    headers={"Authorization": f"Bearer {token_b}"},
                )
            assert list_b.status_code == 200
            assert list_b.json()["total"] == 0
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_facturas_aisladas_por_tenant(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng, TENANT_ID, "tenant-a", "TEN_A")
            await _seed_tenant(eng, TENANT2_ID, "tenant-b", "TEN_B")

            user_a = await _seed_user(eng, TENANT_ID, "finanzas@a.com")
            role_a = await _seed_role(eng, TENANT_ID, "FINANZAS_A", _FINANZAS_PERMISSIONS)
            await _assign_role(eng, user_a.id, role_a.id, TENANT_ID)
            facturante_a = await _seed_user(eng, TENANT_ID, "fact@a.com", facturador=True)

            token_a = create_access_token(
                {"sub": str(user_a.id), "tenant_id": str(TENANT_ID), "roles": ["FINANZAS_A"]},
            )

            async with await _make_app() as client:
                create = await client.post(
                    "/api/facturas",
                    json={
                        "usuario_id": str(facturante_a.id),
                        "periodo": "2026-03",
                        "detalle": "Factura A",
                        "referencia_archivo": "a.pdf",
                    },
                    headers={"Authorization": f"Bearer {token_a}"},
                )
            assert create.status_code == 201

            # Tenant B sees no facturas
            user_b = await _seed_user(eng, TENANT2_ID, "finanzas@b.com")
            role_b = await _seed_role(eng, TENANT2_ID, "FINANZAS_B", _FINANZAS_PERMISSIONS)
            await _assign_role(eng, user_b.id, role_b.id, TENANT2_ID)
            token_b = create_access_token(
                {"sub": str(user_b.id), "tenant_id": str(TENANT2_ID), "roles": ["FINANZAS_B"]},
            )

            async with await _make_app() as client:
                list_b = await client.get(
                    "/api/facturas",
                    headers={"Authorization": f"Bearer {token_b}"},
                )
            assert list_b.status_code == 200
            assert list_b.json()["total"] == 0
        finally:
            await _teardown_db()
            await eng.dispose()


# ═══════════════════════════════════════════════════════════════════════
# 8.12 — Grilla salarial: overlap de vigencia rechazado
# ═══════════════════════════════════════════════════════════════════════

class TestGrillaOverlap:
    """Superposicion de vigencia en SalarioBase rechazada con 409."""

    async def test_overlap_salario_base_rechazado(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["FINANZAS"]},
            )

            async with await _make_app() as client:
                first = await client.post(
                    "/api/liquidaciones/salarios-base",
                    json={
                        "rol": "PROFESOR", "monto": 1000,
                        "desde": "2026-01-01", "hasta": "2026-06-30",
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert first.status_code == 201

            async with await _make_app() as client:
                second = await client.post(
                    "/api/liquidaciones/salarios-base",
                    json={
                        "rol": "PROFESOR", "monto": 1200,
                        "desde": "2026-03-01", "hasta": "2026-09-30",
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert second.status_code == 409
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_sin_overlap_con_mismo_rol_exitoso(self):
        eng = await _make_engine()
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["FINANZAS"]},
            )

            async with await _make_app() as client:
                first = await client.post(
                    "/api/liquidaciones/salarios-base",
                    json={
                        "rol": "PROFESOR", "monto": 1000,
                        "desde": "2026-01-01", "hasta": "2026-01-31",
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert first.status_code == 201

            async with await _make_app() as client:
                second = await client.post(
                    "/api/liquidaciones/salarios-base",
                    json={
                        "rol": "PROFESOR", "monto": 1200,
                        "desde": "2026-02-01", "hasta": "2026-12-31",
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert second.status_code == 201
        finally:
            await _teardown_db()
            await eng.dispose()
