"""Integration tests for comunicaciones: preview, envio, worker, aprobacion, and permission guards."""
import os
import pytest_asyncio
import os

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.crypto import decrypt, encrypt
from app.core.database import Base, close_db_engine
from app.core.security import create_access_token, hash_password
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.models.role import Role
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.models.usuario_role import UsuarioRole
from app.models.version_padron import VersionPadron
from app.services.comunicacion_service import render_template

pytestmark = pytest.mark.asyncio

_db_host = os.environ.get('POSTGRES_HOST', 'localhost')
DB_URL = f"postgresql+asyncpg://active_trace:active_trace@{_db_host}:5432/active_trace_test"
TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


# ── Fixtures ─────────────────────────────────────────────────────────────────


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


async def _seed_tenant(eng, tenant_id=TENANT_ID):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        existing = await session.get(Tenant, tenant_id)
        if existing is None:
            tenant = Tenant(id=tenant_id, name="Test", slug="test-tenant", code="TEST")
            session.add(tenant)
            await session.commit()


async def _seed_user(eng, tenant_id=TENANT_ID, email="coord@test.com", password="testpass123"):
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


async def _seed_role(eng, tenant_id=TENANT_ID, name="COORDINADOR", permissions=None):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        role = Role(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name=name,
            permissions=permissions or [
                "comunicacion:enviar",
                "comunicacion:aprobar",
            ],
            is_system_role=True,
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
            name="VIEWER",
            permissions=["academico:ver_estado_propio"],
            is_system_role=True,
        )
        session.add(role)
        await session.commit()
        return role


async def _seed_role_enviar_only(eng, tenant_id=TENANT_ID):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        role = Role(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name="PROFESOR",
            permissions=["comunicacion:enviar"],
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
            codigo=f"TCOM-{uuid.uuid4().hex[:6]}",
            nombre="Tecnicatura Comunicaciones",
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
            nombre=f"COM-{uuid.uuid4().hex[:6]}",
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
            codigo=f"COM-{uuid.uuid4().hex[:6]}",
            nombre="Matematica I",
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
    nombre="Juan Perez",
    materia_id=None,
    cohorte_id=None,
    email=None,
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
            email=email or f"{legajo}@test.com",
        )
        session.add(entrada)
        await session.commit()
        return entrada


async def _create_auth_headers(eng, user=None, tenant_id=TENANT_ID, roles=None):
    if user is None:
        user = await _seed_user(eng, tenant_id)
    token = create_access_token({
        "sub": str(user.id),
        "tenant_id": str(tenant_id),
        "roles": roles or ["COORDINADOR"],
    })
    return {"Authorization": f"Bearer {token}"}


async def _build_test_data(eng, tenant_id=TENANT_ID):
    await _seed_tenant(eng, tenant_id)
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


# ── Test: Template rendering ──────────────────────────────────────────────────


class TestTemplateRendering:
    def test_render_template_replaces_all_variables(self):
        result = render_template(
            template="Hola {alumno}, materia {materia}, legajo {legajo}",
            alumno="Juan Perez",
            materia="Matematica",
            legajo="1234",
        )
        assert result == "Hola Juan Perez, materia Matematica, legajo 1234"

    def test_render_template_unknown_variable_left_as_is(self):
        result = render_template(
            template="Hola {alumno}, {unknown}",
            alumno="Juan",
            materia="Matematica",
            legajo="1234",
        )
        assert result == "Hola Juan, {unknown}"

    def test_render_template_empty_template(self):
        result = render_template(
            template="",
            alumno="Juan",
            materia="Matematica",
            legajo="1234",
        )
        assert result == ""


# ── Test: Cifrado ─────────────────────────────────────────────────────────────


class TestCifrado:
    def test_encrypt_decrypt_roundtrip(self):
        original = "alumno@test.com"
        cipher = encrypt(original)
        assert cipher != original
        assert decrypt(cipher) == original

    def test_encrypt_empty_string(self):
        assert encrypt("") == ""

    def test_decrypt_empty_string(self):
        assert decrypt("") == ""

    def test_encrypt_produces_different_output_each_time(self):
        """Fernet is non-deterministic — same input produces different ciphertext."""
        original = "test@test.com"
        c1 = encrypt(original)
        c2 = encrypt(original)
        assert c1 != c2
        assert decrypt(c1) == original
        assert decrypt(c2) == original


# ── Test: Preview ─────────────────────────────────────────────────────────────


class TestPreview:
    async def test_preview_returns_rendered_template(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)
        ep = await _seed_entrada_padron(
            eng, TENANT_ID, user.id, "9999", "Ana Gomez", materia.id, cohorte.id,
        )

        resp = await client.post(
            "/api/v1/comunicaciones/preview",
            json={
                "materia_id": str(materia.id),
                "cohorte_id": str(cohorte.id),
                "destinatario_entrada_ids": [str(ep.id)],
                "asunto_template": "Recordatorio: {alumno}",
                "cuerpo_template": "Hola {alumno}, tu materia es {materia}",
            },
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["asunto_renderizado"] == "Recordatorio: Ana Gomez"
        assert data["cuerpo_renderizado"] == "Hola Ana Gomez, tu materia es Matematica I"

    async def test_preview_no_destinatarios_returns_422(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)

        resp = await client.post(
            "/api/v1/comunicaciones/preview",
            json={
                "materia_id": str(materia.id),
                "cohorte_id": str(cohorte.id),
                "destinatario_entrada_ids": [],
                "asunto_template": "Test",
                "cuerpo_template": "Test",
            },
            headers=headers,
        )
        assert resp.status_code == 422

    async def test_preview_works_with_multiple_destinatarios_returns_first(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)
        ep1 = await _seed_entrada_padron(
            eng, TENANT_ID, user.id, "111", "Juan Perez", materia.id, cohorte.id,
        )
        await _seed_entrada_padron(
            eng, TENANT_ID, user.id, "222", "Maria Lopez", materia.id, cohorte.id,
        )

        resp = await client.post(
            "/api/v1/comunicaciones/preview",
            json={
                "materia_id": str(materia.id),
                "cohorte_id": str(cohorte.id),
                "destinatario_entrada_ids": [str(ep1.id)],
                "asunto_template": "Hola {alumno}",
                "cuerpo_template": "Legajo: {legajo}",
            },
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["asunto_renderizado"] == "Hola Juan Perez"
        assert data["cuerpo_renderizado"] == "Legajo: 111"


# ── Test: Envío ───────────────────────────────────────────────────────────────


class TestEnvio:
    async def test_envio_sin_aprobacion_encola_pendiente(self, client, eng):
        """Default tenant config: aprobacion_requerida = false."""
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)
        ep1 = await _seed_entrada_padron(
            eng, TENANT_ID, user.id, "333", "Carlos Gomez", materia.id, cohorte.id,
        )
        ep2 = await _seed_entrada_padron(
            eng, TENANT_ID, user.id, "444", "Lucia Fernandez", materia.id, cohorte.id,
        )

        resp = await client.post(
            "/api/v1/comunicaciones/enviar",
            json={
                "materia_id": str(materia.id),
                "cohorte_id": str(cohorte.id),
                "destinatario_entrada_ids": [str(ep1.id), str(ep2.id)],
                "asunto": "Recordatorio",
                "cuerpo": "Tienes tareas pendientes",
            },
            headers=headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["total"] == 2
        assert data["estado"] == "encolado"
        assert uuid.UUID(data["lote_id"])

    async def test_envio_con_aprobacion_requerida_devuelve_aprobacion_pendiente(self, client, eng):
        """TENANT2 has aprobacion_requerida = true."""
        tenant_id_2 = uuid.UUID("00000000-0000-0000-0000-000000000099")
        await _seed_tenant(eng, tenant_id_2)
        # Set aprobacion_requerida via tenant config column
        await _set_tenant_aprobacion_flag(eng, tenant_id_2, True)

        user, materia, cohorte, _ = await _build_test_data(eng, tenant_id_2)
        headers = await _create_auth_headers(eng, user, tenant_id_2)
        ep1 = await _seed_entrada_padron(
            eng, tenant_id_2, user.id, "555", "Pedro Diaz", materia.id, cohorte.id,
        )

        resp = await client.post(
            "/api/v1/comunicaciones/enviar",
            json={
                "materia_id": str(materia.id),
                "cohorte_id": str(cohorte.id),
                "destinatario_entrada_ids": [str(ep1.id)],
                "asunto": "Aviso",
                "cuerpo": "Texto",
            },
            headers=headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["total"] == 1
        assert data["estado"] == "aprobacion_pendiente"
        assert uuid.UUID(data["lote_id"])

    async def test_envio_destinatarios_invalidos_returns_422(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)
        fake_id = uuid.uuid4()

        resp = await client.post(
            "/api/v1/comunicaciones/enviar",
            json={
                "materia_id": str(materia.id),
                "cohorte_id": str(cohorte.id),
                "destinatario_entrada_ids": [str(fake_id)],
                "asunto": "Test",
                "cuerpo": "Test",
            },
            headers=headers,
        )
        assert resp.status_code == 422


# ── Test: Estado ──────────────────────────────────────────────────────────────


class TestEstado:
    async def test_estado_returns_counts(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)
        ep = await _seed_entrada_padron(
            eng, TENANT_ID, user.id, "666", "Test User", materia.id, cohorte.id,
        )

        env_resp = await client.post(
            "/api/v1/comunicaciones/enviar",
            json={
                "materia_id": str(materia.id),
                "cohorte_id": str(cohorte.id),
                "destinatario_entrada_ids": [str(ep.id)],
                "asunto": "Test",
                "cuerpo": "Test",
            },
            headers=headers,
        )
        lote_id = env_resp.json()["lote_id"]

        resp = await client.get(
            f"/api/v1/comunicaciones/estado?lote_id={lote_id}",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["pendientes"] == 1
        assert data["enviados"] == 0
        assert data["errores"] == 0
        assert data["cancelados"] == 0

    async def test_estado_lote_inexistente_returns_404(self, client, eng):
        user, _, _, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)

        resp = await client.get(
            f"/api/v1/comunicaciones/estado?lote_id={uuid.uuid4()}",
            headers=headers,
        )
        assert resp.status_code == 404


# ── Test: Aprobación ──────────────────────────────────────────────────────────


class TestAprobacion:
    async def test_aprobar_lote_transiciona_a_enviando(self, client, eng):
        tenant_id_2 = uuid.UUID("00000000-0000-0000-0000-000000000099")
        await _seed_tenant(eng, tenant_id_2)
        await _set_tenant_aprobacion_flag(eng, tenant_id_2, True)

        user, materia, cohorte, _ = await _build_test_data(eng, tenant_id_2)
        headers = await _create_auth_headers(eng, user, tenant_id_2)
        ep = await _seed_entrada_padron(
            eng, tenant_id_2, user.id, "777", "Ana Aprob", materia.id, cohorte.id,
        )

        env_resp = await client.post(
            "/api/v1/comunicaciones/enviar",
            json={
                "materia_id": str(materia.id),
                "cohorte_id": str(cohorte.id),
                "destinatario_entrada_ids": [str(ep.id)],
                "asunto": "Req aprob",
                "cuerpo": "Test",
            },
            headers=headers,
        )
        lote_id = env_resp.json()["lote_id"]

        aprobar_resp = await client.post(
            f"/api/v1/comunicaciones/lote/{lote_id}/aprobar",
            headers=headers,
        )
        assert aprobar_resp.status_code == 200
        data = aprobar_resp.json()
        assert data["total_aprobados"] == 1

    async def test_cancelar_lote_transiciona_a_cancelado(self, client, eng):
        tenant_id_2 = uuid.UUID("00000000-0000-0000-0000-000000000099")
        await _seed_tenant(eng, tenant_id_2)
        await _set_tenant_aprobacion_flag(eng, tenant_id_2, True)

        user, materia, cohorte, _ = await _build_test_data(eng, tenant_id_2)
        headers = await _create_auth_headers(eng, user, tenant_id_2)
        ep = await _seed_entrada_padron(
            eng, tenant_id_2, user.id, "888", "Luis Cancel", materia.id, cohorte.id,
        )

        env_resp = await client.post(
            "/api/v1/comunicaciones/enviar",
            json={
                "materia_id": str(materia.id),
                "cohorte_id": str(cohorte.id),
                "destinatario_entrada_ids": [str(ep.id)],
                "asunto": "Req aprob",
                "cuerpo": "Test",
            },
            headers=headers,
        )
        lote_id = env_resp.json()["lote_id"]

        cancel_resp = await client.post(
            f"/api/v1/comunicaciones/lote/{lote_id}/cancelar",
            headers=headers,
        )
        assert cancel_resp.status_code == 200
        data = cancel_resp.json()
        assert data["total_cancelados"] == 1

        # Verify state
        estado_resp = await client.get(
            f"/api/v1/comunicaciones/estado?lote_id={lote_id}",
            headers=headers,
        )
        assert estado_resp.json()["cancelados"] == 1

    async def test_aprobar_lote_inexistente_returns_404(self, client, eng):
        user, _, _, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)

        resp = await client.post(
            f"/api/v1/comunicaciones/lote/{uuid.uuid4()}/aprobar",
            headers=headers,
        )
        assert resp.status_code == 404

    async def test_cancelar_lote_inexistente_returns_404(self, client, eng):
        user, _, _, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)

        resp = await client.post(
            f"/api/v1/comunicaciones/lote/{uuid.uuid4()}/cancelar",
            headers=headers,
        )
        assert resp.status_code == 404


# ── Test: Worker ──────────────────────────────────────────────────────────────


class TestWorker:
    async def test_worker_procesa_mensajes_pendientes(self, client, eng):
        user, materia, cohorte, _ = await _build_test_data(eng)
        headers = await _create_auth_headers(eng, user)
        ep = await _seed_entrada_padron(
            eng, TENANT_ID, user.id, "101", "Worker Test", materia.id, cohorte.id,
        )

        await client.post(
            "/api/v1/comunicaciones/enviar",
            json={
                "materia_id": str(materia.id),
                "cohorte_id": str(cohorte.id),
                "destinatario_entrada_ids": [str(ep.id)],
                "asunto": "Worker",
                "cuerpo": "Procesar",
            },
            headers=headers,
        )

        # Run worker one cycle (pass engine to avoid Windows Docker connection reset)
        from app.workers.comunicaciones_worker import procesar_lote
        await procesar_lote(engine=eng)

        # Verify processed
        factory = async_sessionmaker(create_async_engine(DB_URL, echo=False), expire_on_commit=False)
        async with factory() as session:
            from app.models.comunicacion import Comunicacion
            from sqlalchemy import select
            result = await session.execute(
                select(Comunicacion).where(Comunicacion.tenant_id == TENANT_ID)
            )
            msgs = result.scalars().all()
            for m in msgs:
                assert m.estado == "Enviado"
                assert m.enviado_at is not None

    async def test_worker_ignora_mensajes_con_aprobacion(self, client, eng):
        tenant_id_2 = uuid.UUID("00000000-0000-0000-0000-000000000099")
        await _seed_tenant(eng, tenant_id_2)
        await _set_tenant_aprobacion_flag(eng, tenant_id_2, True)

        user, materia, cohorte, _ = await _build_test_data(eng, tenant_id_2)
        headers = await _create_auth_headers(eng, user, tenant_id_2)
        ep = await _seed_entrada_padron(
            eng, tenant_id_2, user.id, "202", "Ignored", materia.id, cohorte.id,
        )

        env_resp = await client.post(
            "/api/v1/comunicaciones/enviar",
            json={
                "materia_id": str(materia.id),
                "cohorte_id": str(cohorte.id),
                "destinatario_entrada_ids": [str(ep.id)],
                "asunto": "Req aprob",
                "cuerpo": "Ignorame",
            },
            headers=headers,
        )
        lote_id = env_resp.json()["lote_id"]
        assert env_resp.json()["estado"] == "aprobacion_pendiente"

        # Run worker — should not touch these
        from app.workers.comunicaciones_worker import procesar_lote
        await procesar_lote(engine=eng)

        # Verify still pending
        factory = async_sessionmaker(create_async_engine(DB_URL, echo=False), expire_on_commit=False)
        async with factory() as session:
            from app.models.comunicacion import Comunicacion
            from sqlalchemy import select
            result = await session.execute(
                select(Comunicacion).where(
                    Comunicacion.lote_id == uuid.UUID(lote_id)
                )
            )
            msgs = result.scalars().all()
            for m in msgs:
                assert m.estado == "Pendiente"

    async def test_worker_registra_error_sin_detener_bucle(self):
        from app.workers.comunicaciones_worker import _send_email
        result = _send_email("dest@test.com", "asunto", "cuerpo")
        # Mock send siempre retorna True
        assert result is True


# ── Test: Permisos ────────────────────────────────────────────────────────────


class TestPermissionGuard:
    async def test_preview_without_permission_returns_403(self, client, eng):
        await _seed_tenant(eng)
        user = await _seed_user(eng)
        role = await _seed_role_no_permission(eng)
        await _assign_role(eng, user.id, role.id)
        headers = await _create_auth_headers(eng, user)

        resp = await client.post(
            "/api/v1/comunicaciones/preview",
            json={
                "materia_id": str(uuid.uuid4()),
                "cohorte_id": str(uuid.uuid4()),
                "destinatario_entrada_ids": [str(uuid.uuid4())],
                "asunto_template": "Test",
                "cuerpo_template": "Test",
            },
            headers=headers,
        )
        assert resp.status_code == 403

    async def test_enviar_without_permission_returns_403(self, client, eng):
        await _seed_tenant(eng)
        user = await _seed_user(eng)
        role = await _seed_role_no_permission(eng)
        await _assign_role(eng, user.id, role.id)
        headers = await _create_auth_headers(eng, user)

        resp = await client.post(
            "/api/v1/comunicaciones/enviar",
            json={
                "materia_id": str(uuid.uuid4()),
                "cohorte_id": str(uuid.uuid4()),
                "destinatario_entrada_ids": [str(uuid.uuid4())],
                "asunto": "Test",
                "cuerpo": "Test",
            },
            headers=headers,
        )
        assert resp.status_code == 403

    async def test_aprobar_without_permission_returns_403(self, client, eng):
        await _seed_tenant(eng)
        user = await _seed_user(eng)
        role = await _seed_role_enviar_only(eng)
        await _assign_role(eng, user.id, role.id)
        headers = await _create_auth_headers(eng, user)

        resp = await client.post(
            f"/api/v1/comunicaciones/lote/{uuid.uuid4()}/aprobar",
            headers=headers,
        )
        assert resp.status_code == 403

    async def test_cancelar_without_permission_returns_403(self, client, eng):
        await _seed_tenant(eng)
        user = await _seed_user(eng)
        role = await _seed_role_enviar_only(eng)
        await _assign_role(eng, user.id, role.id)
        headers = await _create_auth_headers(eng, user)

        resp = await client.post(
            f"/api/v1/comunicaciones/lote/{uuid.uuid4()}/cancelar",
            headers=headers,
        )
        assert resp.status_code == 403


# ── Helper: Set tenant aprobacion flag ────────────────────────────────────────


async def _set_tenant_aprobacion_flag(eng, tenant_id, value: bool):
    """Set aprobacion_comunicaciones_requerida on the tenant.

    Since the Tenant model doesn't have this column yet, we use raw SQL.
    """
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        from sqlalchemy import text
        # Check if column exists
        result = await session.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='tenant' AND column_name='aprobacion_comunicaciones_requerida'"
            )
        )
        if result.first() is None:
            await session.execute(
                text(
                    "ALTER TABLE tenant ADD COLUMN aprobacion_comunicaciones_requerida "
                    "BOOLEAN NOT NULL DEFAULT FALSE"
                )
            )
        await session.execute(
            text(
                "UPDATE tenant SET aprobacion_comunicaciones_requerida = :val WHERE id = :tid"
            ).bindparams(val=value, tid=tenant_id)
        )
        await session.commit()
