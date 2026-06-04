"""Integration tests for coloquios/evaluaciones endpoints."""

import uuid
from datetime import date, datetime, time, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base, close_db_engine
from app.core.security import create_access_token, hash_password
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.evaluacion import Evaluacion, TipoEvaluacion
from app.models.materia import Materia
from app.models.reserva_evaluacion import EstadoReserva, ReservaEvaluacion
from app.models.role import Role
from app.models.tenant import Tenant
from app.models.turno_disponible import TurnoDisponible
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


async def _seed_materia(eng, tenant_id=TENANT_ID):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        materia = Materia(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            codigo="MAT-101",
            nombre="Matemáticas",
            is_active=True,
        )
        session.add(materia)
        await session.commit()
        return materia


async def _seed_cohorte(eng, tenant_id=TENANT_ID, carrera_id=None):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        if carrera_id is None:
            carrera = Carrera(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                codigo="CARR-001",
                nombre="Test Carrera",
                is_active=True,
            )
            session.add(carrera)
            await session.flush()
            carrera_id = carrera.id

        cohorte = Cohorte(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            carrera_id=carrera_id,
            nombre="2026",
            anio=2026,
            is_active=True,
        )
        session.add(cohorte)
        await session.commit()
        return cohorte


async def _make_app():
    from app.main import create_app
    app = create_app()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


class TestConvocatoriaCrud:
    async def test_create_convocatoria(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["coloquios:gestionar", "coloquios:ver"])
            await _assign_role(eng, user.id, admin_role.id)
            materia = await _seed_materia(eng)
            cohorte = await _seed_cohorte(eng)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )

            async with await _make_app() as client:
                response = await client.post(
                    "/api/coloquios/convocatorias",
                    json={
                        "materia_id": str(materia.id),
                        "cohorte_id": str(cohorte.id),
                        "tipo": "Coloquio",
                        "instancia": "Coloquio Final",
                        "turnos": [
                            {"fecha": "2026-06-15", "hora": "10:00", "cupo_total": 5},
                            {"fecha": "2026-06-16", "hora": "14:00", "cupo_total": 3},
                        ],
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 201
            data = response.json()
            assert data["tipo"] == "Coloquio"
            assert data["instancia"] == "Coloquio Final"
            assert len(data["turnos"]) == 2
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_create_convocatoria_sin_turnos_rejected(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["coloquios:gestionar"])
            await _assign_role(eng, user.id, admin_role.id)
            materia = await _seed_materia(eng)
            cohorte = await _seed_cohorte(eng)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )

            async with await _make_app() as client:
                response = await client.post(
                    "/api/coloquios/convocatorias",
                    json={
                        "materia_id": str(materia.id),
                        "cohorte_id": str(cohorte.id),
                        "tipo": "Coloquio",
                        "instancia": "Coloquio sin turnos",
                        "turnos": [],
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 422
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_list_convocatorias(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["coloquios:gestionar", "coloquios:ver"])
            await _assign_role(eng, user.id, admin_role.id)
            materia = await _seed_materia(eng)
            cohorte = await _seed_cohorte(eng)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )

            async with await _make_app() as client:
                await client.post(
                    "/api/coloquios/convocatorias",
                    json={
                        "materia_id": str(materia.id),
                        "cohorte_id": str(cohorte.id),
                        "tipo": "Coloquio",
                        "instancia": "Coloquio 1",
                        "turnos": [{"fecha": "2026-06-15", "hora": "10:00", "cupo_total": 5}],
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
                await client.post(
                    "/api/coloquios/convocatorias",
                    json={
                        "materia_id": str(materia.id),
                        "cohorte_id": str(cohorte.id),
                        "tipo": "Parcial",
                        "instancia": "Parcial 1",
                        "turnos": [{"fecha": "2026-06-20", "hora": "09:00", "cupo_total": 10}],
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
                response = await client.get(
                    "/api/coloquios/convocatorias",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 2
            assert len(data["items"]) == 2
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_cerrar_convocatoria(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["coloquios:gestionar", "coloquios:ver"])
            await _assign_role(eng, user.id, admin_role.id)
            materia = await _seed_materia(eng)
            cohorte = await _seed_cohorte(eng)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )

            async with await _make_app() as client:
                created = await client.post(
                    "/api/coloquios/convocatorias",
                    json={
                        "materia_id": str(materia.id),
                        "cohorte_id": str(cohorte.id),
                        "tipo": "Coloquio",
                        "instancia": "A cerrar",
                        "turnos": [{"fecha": "2026-06-15", "hora": "10:00", "cupo_total": 5}],
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
                conv_id = created.json()["id"]
                response = await client.post(
                    f"/api/coloquios/convocatorias/{conv_id}/cerrar",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 204
        finally:
            await _teardown_db()
            await eng.dispose()


class TestImportarPadron:
    async def test_importar_padron_exitoso(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            alumno1 = await _seed_user(eng, email="alumno1@test.com")
            alumno2 = await _seed_user(eng, email="alumno2@test.com")
            admin_role = await _seed_role(eng, permissions=["coloquios:gestionar"])
            alumno_role = await _seed_role(eng, name="ALUMNO", permissions=["coloquios:reservar"])
            await _assign_role(eng, user.id, admin_role.id)
            await _assign_role(eng, alumno1.id, alumno_role.id)
            await _assign_role(eng, alumno2.id, alumno_role.id)
            materia = await _seed_materia(eng)
            cohorte = await _seed_cohorte(eng)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )

            async with await _make_app() as client:
                conv = await client.post(
                    "/api/coloquios/convocatorias",
                    json={
                        "materia_id": str(materia.id),
                        "cohorte_id": str(cohorte.id),
                        "tipo": "Coloquio",
                        "instancia": "Import test",
                        "turnos": [{"fecha": "2026-06-15", "hora": "10:00", "cupo_total": 10}],
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
                conv_id = conv.json()["id"]
                response = await client.post(
                    f"/api/coloquios/convocatorias/{conv_id}/importar-alumnos",
                    json={"alumno_ids": [str(alumno1.id), str(alumno2.id)]},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 2
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_importar_padron_usuario_inexistente(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            admin_role = await _seed_role(eng, permissions=["coloquios:gestionar"])
            await _assign_role(eng, user.id, admin_role.id)
            materia = await _seed_materia(eng)
            cohorte = await _seed_cohorte(eng)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )

            async with await _make_app() as client:
                conv = await client.post(
                    "/api/coloquios/convocatorias",
                    json={
                        "materia_id": str(materia.id),
                        "cohorte_id": str(cohorte.id),
                        "tipo": "Coloquio",
                        "instancia": "Import fail",
                        "turnos": [{"fecha": "2026-06-15", "hora": "10:00", "cupo_total": 10}],
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
                conv_id = conv.json()["id"]
                fake_id = uuid.uuid4()
                response = await client.post(
                    f"/api/coloquios/convocatorias/{conv_id}/importar-alumnos",
                    json={"alumno_ids": [str(fake_id)]},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 404
        finally:
            await _teardown_db()
            await eng.dispose()


class TestReservaTurno:
    async def test_reserva_exitosa(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            admin = await _seed_user(eng, email="admin@test.com")
            alumno = await _seed_user(eng, email="alumno@test.com")
            coord_role = await _seed_role(eng, permissions=["coloquios:gestionar", "coloquios:ver"])
            alumno_role = await _seed_role(eng, name="ALUMNO", permissions=["coloquios:reservar"])
            await _assign_role(eng, admin.id, coord_role.id)
            await _assign_role(eng, alumno.id, alumno_role.id)
            materia = await _seed_materia(eng)
            cohorte = await _seed_cohorte(eng)

            admin_token = create_access_token(
                {"sub": str(admin.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            alumno_token = create_access_token(
                {"sub": str(alumno.id), "tenant_id": str(TENANT_ID), "roles": ["ALUMNO"]},
            )

            async with await _make_app() as client:
                conv = await client.post(
                    "/api/coloquios/convocatorias",
                    json={
                        "materia_id": str(materia.id),
                        "cohorte_id": str(cohorte.id),
                        "tipo": "Coloquio",
                        "instancia": "Reserva test",
                        "turnos": [{"fecha": "2026-06-15", "hora": "10:00", "cupo_total": 1}],
                    },
                    headers={"Authorization": f"Bearer {admin_token}"},
                )
                conv_id = conv.json()["id"]
                turno_id = conv.json()["turnos"][0]["id"]

                response = await client.post(
                    f"/api/coloquios/reservas?evaluacion_id={conv_id}",
                    json={"turno_id": str(turno_id)},
                    headers={"Authorization": f"Bearer {alumno_token}"},
                )
            assert response.status_code == 201
            assert response.json()["estado"] == "Activa"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_reserva_cupo_agotado(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            admin = await _seed_user(eng, email="admin@test.com")
            alumno1 = await _seed_user(eng, email="alumno1@test.com")
            alumno2 = await _seed_user(eng, email="alumno2@test.com")
            coord_role = await _seed_role(eng, permissions=["coloquios:gestionar", "coloquios:ver"])
            alumno_role = await _seed_role(eng, name="ALUMNO", permissions=["coloquios:reservar"])
            await _assign_role(eng, admin.id, coord_role.id)
            await _assign_role(eng, alumno1.id, alumno_role.id)
            await _assign_role(eng, alumno2.id, alumno_role.id)
            materia = await _seed_materia(eng)
            cohorte = await _seed_cohorte(eng)

            admin_token = create_access_token(
                {"sub": str(admin.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            token1 = create_access_token(
                {"sub": str(alumno1.id), "tenant_id": str(TENANT_ID), "roles": ["ALUMNO"]},
            )
            token2 = create_access_token(
                {"sub": str(alumno2.id), "tenant_id": str(TENANT_ID), "roles": ["ALUMNO"]},
            )

            async with await _make_app() as client:
                conv = await client.post(
                    "/api/coloquios/convocatorias",
                    json={
                        "materia_id": str(materia.id),
                        "cohorte_id": str(cohorte.id),
                        "tipo": "Coloquio",
                        "instancia": "Cupo test",
                        "turnos": [{"fecha": "2026-06-15", "hora": "10:00", "cupo_total": 1}],
                    },
                    headers={"Authorization": f"Bearer {admin_token}"},
                )
                conv_id = conv.json()["id"]
                turno_id = conv.json()["turnos"][0]["id"]

                await client.post(
                    f"/api/coloquios/reservas?evaluacion_id={conv_id}",
                    json={"turno_id": str(turno_id)},
                    headers={"Authorization": f"Bearer {token1}"},
                )

                response = await client.post(
                    f"/api/coloquios/reservas?evaluacion_id={conv_id}",
                    json={"turno_id": str(turno_id)},
                    headers={"Authorization": f"Bearer {token2}"},
                )
            assert response.status_code == 409
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_reserva_duplicada(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            admin = await _seed_user(eng, email="admin@test.com")
            alumno = await _seed_user(eng, email="alumno@test.com")
            coord_role = await _seed_role(eng, permissions=["coloquios:gestionar", "coloquios:ver"])
            alumno_role = await _seed_role(eng, name="ALUMNO", permissions=["coloquios:reservar"])
            await _assign_role(eng, admin.id, coord_role.id)
            await _assign_role(eng, alumno.id, alumno_role.id)
            materia = await _seed_materia(eng)
            cohorte = await _seed_cohorte(eng)

            admin_token = create_access_token(
                {"sub": str(admin.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            alumno_token = create_access_token(
                {"sub": str(alumno.id), "tenant_id": str(TENANT_ID), "roles": ["ALUMNO"]},
            )

            async with await _make_app() as client:
                conv = await client.post(
                    "/api/coloquios/convocatorias",
                    json={
                        "materia_id": str(materia.id),
                        "cohorte_id": str(cohorte.id),
                        "tipo": "Coloquio",
                        "instancia": "Dupe test",
                        "turnos": [
                            {"fecha": "2026-06-15", "hora": "10:00", "cupo_total": 5},
                            {"fecha": "2026-06-16", "hora": "10:00", "cupo_total": 5},
                        ],
                    },
                    headers={"Authorization": f"Bearer {admin_token}"},
                )
                conv_id = conv.json()["id"]
                turno1_id = conv.json()["turnos"][0]["id"]

                await client.post(
                    f"/api/coloquios/reservas?evaluacion_id={conv_id}",
                    json={"turno_id": str(turno1_id)},
                    headers={"Authorization": f"Bearer {alumno_token}"},
                )

                turno2_id = conv.json()["turnos"][1]["id"]
                response = await client.post(
                    f"/api/coloquios/reservas?evaluacion_id={conv_id}",
                    json={"turno_id": str(turno2_id)},
                    headers={"Authorization": f"Bearer {alumno_token}"},
                )
            assert response.status_code == 409
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_cancelar_reserva_y_reincremento(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            admin = await _seed_user(eng, email="admin@test.com")
            alumno = await _seed_user(eng, email="alumno@test.com")
            coord_role = await _seed_role(eng, permissions=["coloquios:gestionar", "coloquios:ver"])
            alumno_role = await _seed_role(eng, name="ALUMNO", permissions=["coloquios:reservar"])
            await _assign_role(eng, admin.id, coord_role.id)
            await _assign_role(eng, alumno.id, alumno_role.id)
            materia = await _seed_materia(eng)
            cohorte = await _seed_cohorte(eng)

            admin_token = create_access_token(
                {"sub": str(admin.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            alumno_token = create_access_token(
                {"sub": str(alumno.id), "tenant_id": str(TENANT_ID), "roles": ["ALUMNO"]},
            )

            async with await _make_app() as client:
                conv = await client.post(
                    "/api/coloquios/convocatorias",
                    json={
                        "materia_id": str(materia.id),
                        "cohorte_id": str(cohorte.id),
                        "tipo": "Coloquio",
                        "instancia": "Cancel test",
                        "turnos": [{"fecha": "2026-06-15", "hora": "10:00", "cupo_total": 1}],
                    },
                    headers={"Authorization": f"Bearer {admin_token}"},
                )
                conv_id = conv.json()["id"]
                turno_id = conv.json()["turnos"][0]["id"]

                reserva = await client.post(
                    f"/api/coloquios/reservas?evaluacion_id={conv_id}",
                    json={"turno_id": str(turno_id)},
                    headers={"Authorization": f"Bearer {alumno_token}"},
                )
                reserva_id = reserva.json()["id"]

                cancel = await client.patch(
                    f"/api/coloquios/reservas/{reserva_id}/cancelar",
                    headers={"Authorization": f"Bearer {alumno_token}"},
                )
            assert cancel.status_code == 200
        finally:
            await _teardown_db()
            await eng.dispose()


class TestResultados:
    async def test_registrar_resultado_individual(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            admin = await _seed_user(eng, email="admin@test.com")
            alumno = await _seed_user(eng, email="alumno@test.com")
            coord_role = await _seed_role(eng, permissions=["coloquios:gestionar", "coloquios:ver"])
            alumno_role = await _seed_role(eng, name="ALUMNO", permissions=["coloquios:reservar"])
            await _assign_role(eng, admin.id, coord_role.id)
            await _assign_role(eng, alumno.id, alumno_role.id)
            materia = await _seed_materia(eng)
            cohorte = await _seed_cohorte(eng)

            admin_token = create_access_token(
                {"sub": str(admin.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )

            async with await _make_app() as client:
                conv = await client.post(
                    "/api/coloquios/convocatorias",
                    json={
                        "materia_id": str(materia.id),
                        "cohorte_id": str(cohorte.id),
                        "tipo": "Coloquio",
                        "instancia": "Resultado test",
                        "turnos": [{"fecha": "2026-06-15", "hora": "10:00", "cupo_total": 5}],
                    },
                    headers={"Authorization": f"Bearer {admin_token}"},
                )
                conv_id = conv.json()["id"]

                await client.post(
                    f"/api/coloquios/convocatorias/{conv_id}/importar-alumnos",
                    json={"alumno_ids": [str(alumno.id)]},
                    headers={"Authorization": f"Bearer {admin_token}"},
                )

                response = await client.post(
                    f"/api/coloquios/resultados?evaluacion_id={conv_id}",
                    json={"alumno_id": str(alumno.id), "nota_final": "8.50"},
                    headers={"Authorization": f"Bearer {admin_token}"},
                )
            assert response.status_code == 201
            assert response.json()["nota_final"] == "8.50"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_registrar_resultados_batch(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            admin = await _seed_user(eng, email="admin@test.com")
            alumno1 = await _seed_user(eng, email="a1@test.com")
            alumno2 = await _seed_user(eng, email="a2@test.com")
            coord_role = await _seed_role(eng, permissions=["coloquios:gestionar", "coloquios:ver"])
            alumno_role = await _seed_role(eng, name="ALUMNO", permissions=["coloquios:reservar"])
            await _assign_role(eng, admin.id, coord_role.id)
            await _assign_role(eng, alumno1.id, alumno_role.id)
            await _assign_role(eng, alumno2.id, alumno_role.id)
            materia = await _seed_materia(eng)
            cohorte = await _seed_cohorte(eng)

            admin_token = create_access_token(
                {"sub": str(admin.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )

            async with await _make_app() as client:
                conv = await client.post(
                    "/api/coloquios/convocatorias",
                    json={
                        "materia_id": str(materia.id),
                        "cohorte_id": str(cohorte.id),
                        "tipo": "Coloquio",
                        "instancia": "Batch test",
                        "turnos": [{"fecha": "2026-06-15", "hora": "10:00", "cupo_total": 5}],
                    },
                    headers={"Authorization": f"Bearer {admin_token}"},
                )
                conv_id = conv.json()["id"]

                await client.post(
                    f"/api/coloquios/convocatorias/{conv_id}/importar-alumnos",
                    json={"alumno_ids": [str(alumno1.id), str(alumno2.id)]},
                    headers={"Authorization": f"Bearer {admin_token}"},
                )

                response = await client.post(
                    f"/api/coloquios/resultados/batch?evaluacion_id={conv_id}",
                    json={
                        "items": [
                            {"alumno_id": str(alumno1.id), "nota_final": "8"},
                            {"alumno_id": str(alumno2.id), "nota_final": "7"},
                        ]
                    },
                    headers={"Authorization": f"Bearer {admin_token}"},
                )
            assert response.status_code == 201
            assert response.json()["count"] == 2
        finally:
            await _teardown_db()
            await eng.dispose()


class TestMetricas:
    async def test_obtener_metricas(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            admin = await _seed_user(eng, email="admin@test.com")
            coord_role = await _seed_role(eng, permissions=["coloquios:gestionar", "coloquios:ver"])
            await _assign_role(eng, admin.id, coord_role.id)
            materia = await _seed_materia(eng)
            cohorte = await _seed_cohorte(eng)

            admin_token = create_access_token(
                {"sub": str(admin.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )

            async with await _make_app() as client:
                response = await client.get(
                    "/api/coloquios/metricas",
                    headers={"Authorization": f"Bearer {admin_token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert "total_alumnos" in data
            assert "instancias_activas" in data
            assert "reservas_activas" in data
            assert "notas_registradas" in data
        finally:
            await _teardown_db()
            await eng.dispose()


class TestPermissionGuard:
    async def test_alumno_no_puede_gestionar(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            alumno = await _seed_user(eng, email="alumno@test.com")
            alumno_role = await _seed_role(eng, name="ALUMNO", permissions=["coloquios:reservar"])
            await _assign_role(eng, alumno.id, alumno_role.id)
            token = create_access_token(
                {"sub": str(alumno.id), "tenant_id": str(TENANT_ID), "roles": ["ALUMNO"]},
            )

            async with await _make_app() as client:
                response = await client.get(
                    "/api/coloquios/convocatorias",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_coordinador_no_puede_reservar_sin_permiso(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            coord = await _seed_user(eng, email="coord@test.com")
            coord_role = await _seed_role(eng, permissions=["coloquios:gestionar", "coloquios:ver"])
            await _assign_role(eng, coord.id, coord_role.id)
            token = create_access_token(
                {"sub": str(coord.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )

            async with await _make_app() as client:
                response = await client.post(
                    "/api/coloquios/reservas?evaluacion_id=" + str(uuid.uuid4()),
                    json={"turno_id": str(uuid.uuid4())},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()
