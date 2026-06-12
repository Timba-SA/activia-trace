import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import close_db_engine
from app.models.audit_log import AuditLog
from app.models.materia import Materia
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.repositories.audit_log_repository import AuditLogRepository

pytestmark = pytest.mark.asyncio

_db_host = os.environ.get('POSTGRES_HOST', 'localhost')
DB_URL = f"postgresql+asyncpg://active_trace:active_trace@{_db_host}:5432/active_trace_test"

TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
TENANT2_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


async def _setup_db():
    from app.core.database import Base
    eng = create_async_engine(DB_URL, echo=False)
    async with eng.begin() as conn:
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


class TestCountByDay:
    async def test_groups_by_date(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                today = datetime.now(timezone.utc).replace(hour=10, minute=0, second=0, microsecond=0)
                yesterday = today - timedelta(days=1)
                for i in range(3):
                    await repo.create(
                        tenant_id=TENANT_ID, actor_id=user.id, accion="TEST",
                        fecha_hora=today,
                    )
                await repo.create(
                    tenant_id=TENANT_ID, actor_id=user.id, accion="TEST",
                    fecha_hora=yesterday,
                )
                await session.commit()

            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                results = await repo.count_by_day()
                assert len(results) == 2
                day_map = {str(r["fecha"]): r["cantidad"] for r in results}
                assert list(day_map.values()) == sorted(day_map.values())
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_filters_by_date_range(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                today = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
                for i in range(5):
                    await repo.create(
                        tenant_id=TENANT_ID, actor_id=user.id, accion="TEST",
                        fecha_hora=today - timedelta(days=i),
                    )
                await session.commit()

            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                desde = today - timedelta(days=2)
                hasta = today
                results = await repo.count_by_day(desde=desde, hasta=hasta)
                assert len(results) == 3
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

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                now = datetime.now(timezone.utc)
                for i in range(2):
                    await repo.create(
                        tenant_id=TENANT_ID, actor_id=user.id, accion="TEST",
                        materia_id=materia.id, fecha_hora=now,
                    )
                await repo.create(
                    tenant_id=TENANT_ID, actor_id=user.id, accion="TEST",
                    fecha_hora=now,
                )
                await session.commit()

            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                results = await repo.count_by_day(materia_id=materia.id)
                assert len(results) == 1
                assert results[0]["cantidad"] == 2
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_filters_by_actor(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user1 = await _seed_user(eng)
            user2 = await _seed_user(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                now = datetime.now(timezone.utc)
                for i in range(3):
                    await repo.create(
                        tenant_id=TENANT_ID, actor_id=user1.id, accion="TEST",
                        fecha_hora=now,
                    )
                await repo.create(
                    tenant_id=TENANT_ID, actor_id=user2.id, accion="TEST",
                    fecha_hora=now,
                )
                await session.commit()

            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                results = await repo.count_by_day(actor_id=user1.id)
                assert len(results) == 1
                assert results[0]["cantidad"] == 3
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_tenant_isolation(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            await _seed_tenant(eng, TENANT2_ID)
            user = await _seed_user(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                now = datetime.now(timezone.utc)
                await repo.create(
                    tenant_id=TENANT_ID, actor_id=user.id, accion="T1",
                    fecha_hora=now,
                )
                await session.commit()

            async with factory() as session:
                repo = AuditLogRepository(session, TENANT2_ID)
                await repo.create(
                    tenant_id=TENANT2_ID, actor_id=user.id, accion="T2",
                    fecha_hora=now,
                )
                await session.commit()

            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                results = await repo.count_by_day()
                for r in results:
                    assert r["cantidad"] == 1

            async with factory() as session:
                repo2 = AuditLogRepository(session, TENANT2_ID)
                results2 = await repo2.count_by_day()
                assert len(results2) == 1
        finally:
            await _teardown_db()
            await eng.dispose()


class TestCountByActor:
    async def test_groups_by_actor_with_breakdown(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                now = datetime.now(timezone.utc)
                await repo.create(tenant_id=TENANT_ID, actor_id=user.id, accion="ACCION_A", fecha_hora=now)
                await repo.create(tenant_id=TENANT_ID, actor_id=user.id, accion="ACCION_A", fecha_hora=now)
                await repo.create(tenant_id=TENANT_ID, actor_id=user.id, accion="ACCION_B", fecha_hora=now)
                await session.commit()

            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                results = await repo.count_by_actor()
                assert len(results) == 1
                assert results[0]["actor_id"] == user.id
                assert results[0]["total"] == 3
                assert results[0]["detalle_por_accion"] == {"ACCION_A": 2, "ACCION_B": 1}
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_multiple_actors(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user1 = await _seed_user(eng)
            user2 = await _seed_user(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                now = datetime.now(timezone.utc)
                await repo.create(tenant_id=TENANT_ID, actor_id=user1.id, accion="ACCION_X", fecha_hora=now)
                await repo.create(tenant_id=TENANT_ID, actor_id=user2.id, accion="ACCION_Y", fecha_hora=now)
                await session.commit()

            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                results = await repo.count_by_actor()
                assert len(results) == 2
                actor_map = {r["actor_id"]: r for r in results}
                assert actor_map[user1.id]["total"] == 1
                assert actor_map[user2.id]["total"] == 1
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_tenant_isolation(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            await _seed_tenant(eng, TENANT2_ID)
            user = await _seed_user(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                now = datetime.now(timezone.utc)
                await repo.create(tenant_id=TENANT_ID, actor_id=user.id, accion="T1", fecha_hora=now)
                await session.commit()

            async with factory() as session:
                repo = AuditLogRepository(session, TENANT2_ID)
                await repo.create(tenant_id=TENANT2_ID, actor_id=user.id, accion="T2", fecha_hora=now)
                await session.commit()

            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                results = await repo.count_by_actor()
                assert len(results) == 1
                assert len(results[0]["detalle_por_accion"]) == 1

            async with factory() as session:
                repo2 = AuditLogRepository(session, TENANT2_ID)
                results2 = await repo2.count_by_actor()
                assert len(results2) == 1
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_filters_by_date_range(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                now = datetime.now(timezone.utc)
                await repo.create(tenant_id=TENANT_ID, actor_id=user.id, accion="HOY", fecha_hora=now)
                await repo.create(tenant_id=TENANT_ID, actor_id=user.id, accion="ANTIGUO", fecha_hora=now - timedelta(days=10))
                await session.commit()

            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                results = await repo.count_by_actor(
                    desde=now - timedelta(hours=1),
                    hasta=now + timedelta(hours=1),
                )
                assert len(results) == 1
                assert results[0]["detalle_por_accion"] == {"HOY": 1}
        finally:
            await _teardown_db()
            await eng.dispose()


class TestCountByActorMateria:
    async def test_groups_by_actor_and_materia(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            materia = await _seed_materia(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                now = datetime.now(timezone.utc)
                for i in range(3):
                    await repo.create(
                        tenant_id=TENANT_ID, actor_id=user.id, accion="TEST",
                        materia_id=materia.id, fecha_hora=now,
                    )
                await repo.create(
                    tenant_id=TENANT_ID, actor_id=user.id, accion="TEST",
                    fecha_hora=now,
                )
                await session.commit()

            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                results = await repo.count_by_actor_materia()
                assert len(results) == 2
                materia_result = [r for r in results if r["materia_id"] == materia.id]
                assert len(materia_result) == 1
                assert materia_result[0]["total"] == 3
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_ordered_by_total_desc(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            mat1 = await _seed_materia(eng)
            mat2 = await _seed_materia(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                now = datetime.now(timezone.utc)
                for i in range(5):
                    await repo.create(
                        tenant_id=TENANT_ID, actor_id=user.id, accion="TEST",
                        materia_id=mat1.id, fecha_hora=now,
                    )
                await repo.create(
                    tenant_id=TENANT_ID, actor_id=user.id, accion="TEST",
                    materia_id=mat2.id, fecha_hora=now,
                )
                await session.commit()

            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                results = await repo.count_by_actor_materia()
                assert results[0]["total"] >= results[-1]["total"]
                assert results[0]["materia_id"] == mat1.id
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_tenant_isolation(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            await _seed_tenant(eng, TENANT2_ID)
            user = await _seed_user(eng)
            materia = await _seed_materia(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                now = datetime.now(timezone.utc)
                await repo.create(
                    tenant_id=TENANT_ID, actor_id=user.id, accion="T1",
                    materia_id=materia.id, fecha_hora=now,
                )
                await session.commit()

            async with factory() as session:
                repo = AuditLogRepository(session, TENANT2_ID)
                await repo.create(
                    tenant_id=TENANT2_ID, actor_id=user.id, accion="T2",
                    materia_id=materia.id, fecha_hora=now,
                )
                await session.commit()

            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                results = await repo.count_by_actor_materia()
                assert len(results) == 1

            async with factory() as session:
                repo2 = AuditLogRepository(session, TENANT2_ID)
                results2 = await repo2.count_by_actor_materia()
                assert len(results2) == 1
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_filters_by_date_range(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            materia = await _seed_materia(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                now = datetime.now(timezone.utc)
                await repo.create(
                    tenant_id=TENANT_ID, actor_id=user.id, accion="TEST",
                    materia_id=materia.id, fecha_hora=now,
                )
                await repo.create(
                    tenant_id=TENANT_ID, actor_id=user.id, accion="TEST",
                    materia_id=materia.id, fecha_hora=now - timedelta(days=10),
                )
                await session.commit()

            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                results = await repo.count_by_actor_materia(
                    desde=now - timedelta(hours=1),
                    hasta=now + timedelta(hours=1),
                )
                assert len(results) == 1
                assert results[0]["total"] == 1
        finally:
            await _teardown_db()
            await eng.dispose()
