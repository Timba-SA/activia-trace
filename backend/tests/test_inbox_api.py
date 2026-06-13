"""Integration tests for inbox (mensajería interna) endpoints."""
import os
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base, close_db_engine
from app.core.security import create_access_token, hash_password
from tests.db_utils import drop_enum_types
from app.models.mensaje import Mensaje
from app.models.tenant import Tenant
from app.models.usuario import Usuario

pytestmark = pytest.mark.asyncio

_db_host = os.environ.get('POSTGRES_HOST', 'localhost')
DB_URL = f"postgresql+asyncpg://active_trace:active_trace@{_db_host}:5432/active_trace_test"
TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
TENANT_B_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


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


async def _make_client():
    from app.main import create_app
    app = create_app()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


class TestInbox:
    async def test_send_message_creates_and_returns_it(self):
        await close_db_engine()
        eng = create_async_engine(DB_URL, echo=False)
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await drop_enum_types(conn)
            await conn.run_sync(Base.metadata.create_all)
        factory = async_sessionmaker(eng, expire_on_commit=False)

        async with factory() as session:
            tenant = Tenant(id=TENANT_ID, name="Test", slug="test-tenant", code="TEST")
            session.add(tenant)
            sender = Usuario(
                id=uuid.uuid4(),
                tenant_id=TENANT_ID,
                email="sender@test.com",
                hashed_password=hash_password("testpass"),
                is_active=True,
            )
            recipient = Usuario(
                id=uuid.uuid4(),
                tenant_id=TENANT_ID,
                email="recipient@test.com",
                hashed_password=hash_password("testpass"),
                is_active=True,
            )
            session.add(sender)
            session.add(recipient)
            await session.commit()
            sender_id = sender.id
            recipient_id = recipient.id

        token = create_access_token({"sub": str(sender_id), "tenant_id": str(TENANT_ID), "roles": []})
        headers = {"Authorization": f"Bearer {token}"}

        client = await _make_client()
        try:
            resp = await client.post(
                "/api/inbox",
                json={"destinatario_id": str(recipient_id), "asunto": "Test", "cuerpo": "Hello"},
                headers=headers,
            )
            assert resp.status_code == 201, resp.text
            data = resp.json()
            assert data["asunto"] == "Test"
            assert data["cuerpo"] == "Hello"
            assert data["remitente_id"] == str(sender_id)
            assert data["destinatario_id"] == str(recipient_id)
            assert data["hilo_id"] is not None
            assert data["leido"] is False
        finally:
            await client.aclose()

        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await eng.dispose()

    async def test_list_inbox_returns_messages(self):
        await close_db_engine()
        eng = create_async_engine(DB_URL, echo=False)
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await drop_enum_types(conn)
            await conn.run_sync(Base.metadata.create_all)
        factory = async_sessionmaker(eng, expire_on_commit=False)

        async with factory() as session:
            tenant = Tenant(id=TENANT_ID, name="Test", slug="test-tenant", code="TEST")
            session.add(tenant)
            sender = Usuario(id=uuid.uuid4(), tenant_id=TENANT_ID, email="sender@test.com",
                             hashed_password=hash_password("testpass"), is_active=True)
            recipient = Usuario(id=uuid.uuid4(), tenant_id=TENANT_ID, email="recip@test.com",
                                hashed_password=hash_password("testpass"), is_active=True)
            session.add(sender)
            session.add(recipient)
            await session.commit()
            sender_id, recipient_id = sender.id, recipient.id

            hilo = uuid.uuid4()
            msg1 = Mensaje(id=uuid.uuid4(), tenant_id=TENANT_ID, remitente_id=sender_id,
                           destinatario_id=recipient_id, hilo_id=hilo, asunto="First", cuerpo="Body 1")
            msg2 = Mensaje(id=uuid.uuid4(), tenant_id=TENANT_ID, remitente_id=sender_id,
                           destinatario_id=recipient_id, hilo_id=hilo, asunto="Second", cuerpo="Body 2")
            session.add(msg1)
            session.add(msg2)
            await session.commit()

        token = create_access_token({"sub": str(recipient_id), "tenant_id": str(TENANT_ID), "roles": []})
        headers = {"Authorization": f"Bearer {token}"}

        client = await _make_client()
        try:
            resp = await client.get("/api/inbox", headers=headers)
            assert resp.status_code == 200, resp.text
            data = resp.json()
            assert data["total"] == 2
            assert len(data["items"]) == 2
        finally:
            await client.aclose()

        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await eng.dispose()

    async def test_get_message_marks_as_leido(self):
        await close_db_engine()
        eng = create_async_engine(DB_URL, echo=False)
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await drop_enum_types(conn)
            await conn.run_sync(Base.metadata.create_all)
        factory = async_sessionmaker(eng, expire_on_commit=False)

        async with factory() as session:
            tenant = Tenant(id=TENANT_ID, name="Test", slug="test-tenant", code="TEST")
            session.add(tenant)
            sender = Usuario(id=uuid.uuid4(), tenant_id=TENANT_ID, email="sender@test.com",
                             hashed_password=hash_password("testpass"), is_active=True)
            recipient = Usuario(id=uuid.uuid4(), tenant_id=TENANT_ID, email="recip@test.com",
                                hashed_password=hash_password("testpass"), is_active=True)
            session.add(sender)
            session.add(recipient)
            await session.commit()
            msg = Mensaje(id=uuid.uuid4(), tenant_id=TENANT_ID, remitente_id=sender.id,
                          destinatario_id=recipient.id, hilo_id=uuid.uuid4(),
                          asunto="Test", cuerpo="Body")
            session.add(msg)
            await session.commit()
            msg_id = msg.id
            recip_id = recipient.id

        token = create_access_token({"sub": str(recip_id), "tenant_id": str(TENANT_ID), "roles": []})
        headers = {"Authorization": f"Bearer {token}"}

        client = await _make_client()
        try:
            resp = await client.get(f"/api/inbox/{msg_id}", headers=headers)
            assert resp.status_code == 200, resp.text
            data = resp.json()
            assert data["leido"] is True
        finally:
            await client.aclose()

        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await eng.dispose()

    async def test_reply_creates_message_in_same_thread(self):
        await close_db_engine()
        eng = create_async_engine(DB_URL, echo=False)
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await drop_enum_types(conn)
            await conn.run_sync(Base.metadata.create_all)
        factory = async_sessionmaker(eng, expire_on_commit=False)

        async with factory() as session:
            tenant = Tenant(id=TENANT_ID, name="Test", slug="test-tenant", code="TEST")
            session.add(tenant)
            sender = Usuario(id=uuid.uuid4(), tenant_id=TENANT_ID, email="sender@test.com",
                             hashed_password=hash_password("testpass"), is_active=True)
            recipient = Usuario(id=uuid.uuid4(), tenant_id=TENANT_ID, email="recip@test.com",
                                hashed_password=hash_password("testpass"), is_active=True)
            session.add(sender)
            session.add(recipient)
            await session.commit()
            hilo = uuid.uuid4()
            original = Mensaje(id=uuid.uuid4(), tenant_id=TENANT_ID, remitente_id=sender.id,
                               destinatario_id=recipient.id, hilo_id=hilo,
                               asunto="Original", cuerpo="Original body")
            session.add(original)
            await session.commit()
            msg_id, recip_id, sender_id = original.id, recipient.id, sender.id

        token = create_access_token({"sub": str(recip_id), "tenant_id": str(TENANT_ID), "roles": []})
        headers = {"Authorization": f"Bearer {token}"}

        client = await _make_client()
        try:
            resp = await client.post(
                f"/api/inbox/{msg_id}/responder",
                json={"cuerpo": "Reply body"},
                headers=headers,
            )
            assert resp.status_code == 201, resp.text
            data = resp.json()
            assert data["cuerpo"] == "Reply body"
            assert data["hilo_id"] is not None
            assert data["asunto"] == "Original"
            assert data["destinatario_id"] == str(sender_id)
        finally:
            await client.aclose()

        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await eng.dispose()

    async def test_send_to_nonexistent_user_returns_404(self):
        await close_db_engine()
        eng = create_async_engine(DB_URL, echo=False)
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await drop_enum_types(conn)
            await conn.run_sync(Base.metadata.create_all)
        factory = async_sessionmaker(eng, expire_on_commit=False)

        async with factory() as session:
            tenant = Tenant(id=TENANT_ID, name="Test", slug="test-tenant", code="TEST")
            session.add(tenant)
            sender = Usuario(id=uuid.uuid4(), tenant_id=TENANT_ID, email="sender@test.com",
                             hashed_password=hash_password("testpass"), is_active=True)
            session.add(sender)
            await session.commit()
            sender_id = sender.id

        token = create_access_token({"sub": str(sender_id), "tenant_id": str(TENANT_ID), "roles": []})
        headers = {"Authorization": f"Bearer {token}"}

        fake_id = uuid.uuid4()
        client = await _make_client()
        try:
            resp = await client.post(
                "/api/inbox",
                json={"destinatario_id": str(fake_id), "asunto": "Test", "cuerpo": "Hello"},
                headers=headers,
            )
            assert resp.status_code == 404, resp.text
        finally:
            await client.aclose()

        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await eng.dispose()

    async def test_send_to_self_returns_422(self):
        await close_db_engine()
        eng = create_async_engine(DB_URL, echo=False)
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await drop_enum_types(conn)
            await conn.run_sync(Base.metadata.create_all)
        factory = async_sessionmaker(eng, expire_on_commit=False)

        async with factory() as session:
            tenant = Tenant(id=TENANT_ID, name="Test", slug="test-tenant", code="TEST")
            session.add(tenant)
            sender = Usuario(id=uuid.uuid4(), tenant_id=TENANT_ID, email="sender@test.com",
                             hashed_password=hash_password("testpass"), is_active=True)
            session.add(sender)
            await session.commit()
            sender_id = sender.id

        token = create_access_token({"sub": str(sender_id), "tenant_id": str(TENANT_ID), "roles": []})
        headers = {"Authorization": f"Bearer {token}"}

        client = await _make_client()
        try:
            resp = await client.post(
                "/api/inbox",
                json={"destinatario_id": str(sender_id), "asunto": "Test", "cuerpo": "Hello"},
                headers=headers,
            )
            assert resp.status_code == 422, resp.text
        finally:
            await client.aclose()

        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await eng.dispose()

    async def test_tenant_isolation_blocks_cross_tenant_messaging(self):
        await close_db_engine()
        eng = create_async_engine(DB_URL, echo=False)
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await drop_enum_types(conn)
            await conn.run_sync(Base.metadata.create_all)
        factory = async_sessionmaker(eng, expire_on_commit=False)

        async with factory() as session:
            tenant_a = Tenant(id=TENANT_ID, name="Tenant A", slug="tenant-a", code="TA")
            tenant_b = Tenant(id=TENANT_B_ID, name="Tenant B", slug="tenant-b", code="TB")
            session.add(tenant_a)
            session.add(tenant_b)
            user_a = Usuario(id=uuid.uuid4(), tenant_id=TENANT_ID, email="a@test.com",
                             hashed_password=hash_password("pass"), is_active=True)
            user_b = Usuario(id=uuid.uuid4(), tenant_id=TENANT_B_ID, email="b@test.com",
                             hashed_password=hash_password("pass"), is_active=True)
            session.add(user_a)
            session.add(user_b)
            await session.commit()
            user_a_id, user_b_id = user_a.id, user_b.id

        token = create_access_token({"sub": str(user_a_id), "tenant_id": str(TENANT_ID), "roles": []})
        headers = {"Authorization": f"Bearer {token}"}

        client = await _make_client()
        try:
            resp = await client.post(
                "/api/inbox",
                json={"destinatario_id": str(user_b_id), "asunto": "Cross", "cuerpo": "Test"},
                headers=headers,
            )
            assert resp.status_code == 404, resp.text
        finally:
            await client.aclose()

        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await eng.dispose()
