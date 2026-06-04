import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.audit_constants import AuditActionCode
from app.core.audit_context import AuditContext as AuditContextCls
from app.core.database import close_db_engine
from app.models.audit_log import AuditLog
from app.models.materia import Materia
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.repositories.audit_log_repository import AuditLogRepository
from app.services.audit_service import AuditService

pytestmark = pytest.mark.asyncio

DB_URL = "postgresql+asyncpg://active_trace:active_trace@localhost:5432/active_trace_test"

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


# ===== Group 1: Model + Migration =====


class TestAuditLogModel:
    async def test_create_audit_log_with_all_fields(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            materia = await _seed_materia(eng)
            now = datetime.now(timezone.utc)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                log = AuditLog(
                    tenant_id=TENANT_ID,
                    actor_id=user.id,
                    materia_id=materia.id,
                    accion="CALIFICACIONES_IMPORTAR",
                    detalle={"file": "calificaciones.xlsx", "count": 50},
                    filas_afectadas=42,
                    ip="192.168.1.1",
                    user_agent="Mozilla/5.0",
                    fecha_hora=now,
                )
                session.add(log)
                await session.flush()
                assert log.id is not None
                assert log.tenant_id == TENANT_ID
                assert log.actor_id == user.id
                assert log.materia_id == materia.id
                assert log.accion == "CALIFICACIONES_IMPORTAR"
                assert log.detalle == {"file": "calificaciones.xlsx", "count": 50}
                assert log.filas_afectadas == 42
                assert log.ip == "192.168.1.1"
                assert log.user_agent == "Mozilla/5.0"
                assert log.fecha_hora == now
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_create_audit_log_with_minimal_fields(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                log = AuditLog(
                    tenant_id=TENANT_ID,
                    actor_id=user.id,
                    accion="PADRON_CARGAR",
                )
                session.add(log)
                await session.flush()
                assert log.filas_afectadas == 0
                assert log.detalle is None
                assert log.impersonado_id is None
                assert log.materia_id is None
                assert log.ip is None
                assert log.user_agent is None
                assert log.fecha_hora is not None
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_audit_log_assigned_to_materia(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            materia = await _seed_materia(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                log = AuditLog(
                    tenant_id=TENANT_ID,
                    actor_id=user.id,
                    materia_id=materia.id,
                    accion="COMUNICACION_ENVIAR",
                )
                session.add(log)
                await session.flush()
                assert log.materia_id == materia.id
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_append_only_trigger_rejects_update(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            await _setup_trigger(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                log = AuditLog(
                    tenant_id=TENANT_ID,
                    actor_id=user.id,
                    accion="TEST_UPDATE_REJECT",
                )
                session.add(log)
                await session.commit()

                stmt = sa.text("UPDATE audit_log SET accion = 'CHANGED' WHERE id = :id")
                stmt = stmt.bindparams(id=log.id)
                with pytest.raises(Exception, match="append_only"):
                    await session.execute(stmt)
                    await session.commit()
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_append_only_trigger_rejects_delete(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            await _setup_trigger(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                log = AuditLog(
                    tenant_id=TENANT_ID,
                    actor_id=user.id,
                    accion="TEST_DELETE_REJECT",
                )
                session.add(log)
                await session.commit()

                stmt = sa.text("DELETE FROM audit_log WHERE id = :id")
                stmt = stmt.bindparams(id=log.id)
                with pytest.raises(Exception, match="append_only"):
                    await session.execute(stmt)
                    await session.commit()
        finally:
            await _teardown_db()
            await eng.dispose()


class TestAuditLogRepository:
    async def test_create_and_find(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                log = await repo.create(
                    tenant_id=TENANT_ID,
                    actor_id=user.id,
                    accion="ASIGNACION_MODIFICAR",
                    filas_afectadas=10,
                )
                assert log.id is not None
                assert log.accion == "ASIGNACION_MODIFICAR"
                assert log.filas_afectadas == 10

                items, total, pages = await repo.find(accion="ASIGNACION_MODIFICAR")
                assert total >= 1
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_repository_update_raises(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                log = await repo.create(
                    tenant_id=TENANT_ID,
                    actor_id=user.id,
                    accion="TEST",
                )
                with pytest.raises(NotImplementedError, match="append-only"):
                    await repo.update(log.id, accion="CHANGED")
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_repository_soft_delete_raises(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                log = await repo.create(
                    tenant_id=TENANT_ID,
                    actor_id=user.id,
                    accion="TEST",
                )
                with pytest.raises(NotImplementedError, match="append-only"):
                    await repo.soft_delete(log.id)
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_find_filters_by_tenant(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            await _seed_tenant(eng, TENANT2_ID)
            user = await _seed_user(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                await repo.create(
                    tenant_id=TENANT_ID, actor_id=user.id, accion="T1"
                )
                await repo.create(
                    tenant_id=TENANT_ID, actor_id=user.id, accion="T2"
                )
                items, total, pages = await repo.find()
                assert total == 2

            async with factory() as session:
                repo2 = AuditLogRepository(session, TENANT2_ID)
                items2, total2, pages2 = await repo2.find()
                assert total2 == 0
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_find_with_all_filters(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            materia = await _seed_materia(eng)
            from datetime import timedelta

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                await repo.create(
                    tenant_id=TENANT_ID,
                    actor_id=user.id,
                    materia_id=materia.id,
                    accion="FILTER_TEST",
                    fecha_hora=datetime.now(timezone.utc),
                )
                await repo.create(
                    tenant_id=TENANT_ID,
                    actor_id=user.id,
                    accion="OTHER",
                    fecha_hora=datetime.now(timezone.utc) - timedelta(days=10),
                )
                await session.commit()
                repo = AuditLogRepository(session, TENANT_ID)
                items, total, pages = await repo.find(
                    accion="FILTER_TEST",
                    actor_id=user.id,
                    materia_id=materia.id,
                    desde=datetime.now(timezone.utc) - timedelta(hours=1),
                    hasta=datetime.now(timezone.utc) + timedelta(hours=1),
                )
                assert total == 1
        finally:
            await _teardown_db()
            await eng.dispose()


# ===== Group 2: Constants =====


class TestAuditActionCode:
    def test_contains_standard_codes(self):
        assert hasattr(AuditActionCode, "PADRON_CARGAR")
        assert hasattr(AuditActionCode, "CALIFICACIONES_IMPORTAR")
        assert hasattr(AuditActionCode, "COMUNICACION_ENVIAR")
        assert hasattr(AuditActionCode, "LIQUIDACION_CERRAR")
        assert hasattr(AuditActionCode, "IMPERSONACION_INICIAR")
        assert hasattr(AuditActionCode, "IMPERSONACION_FINALIZAR")
        assert hasattr(AuditActionCode, "ASIGNACION_MODIFICAR")

    def test_action_codes_are_strings(self):
        assert isinstance(AuditActionCode.PADRON_CARGAR, str)
        assert isinstance(AuditActionCode.CALIFICACIONES_IMPORTAR, str)
        assert isinstance(AuditActionCode.COMUNICACION_ENVIAR, str)
        assert isinstance(AuditActionCode.LIQUIDACION_CERRAR, str)
        assert isinstance(AuditActionCode.IMPERSONACION_INICIAR, str)
        assert isinstance(AuditActionCode.IMPERSONACION_FINALIZAR, str)


# ===== Group 3: AuditContext + AuditService =====


async def _setup_trigger(eng):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        await session.execute(sa.text("""
            CREATE OR REPLACE FUNCTION audit_log_append_only()
            RETURNS TRIGGER AS $$
            BEGIN
                RAISE EXCEPTION 'append_only: audit_log does not support UPDATE or DELETE'
                USING HINT = 'Audit log is append-only. INSERT only.';
            END;
            $$ LANGUAGE plpgsql;
        """))
        await session.execute(sa.text("""
            DROP TRIGGER IF EXISTS trg_audit_log_append_only ON audit_log
        """))
        await session.execute(sa.text("""
            CREATE TRIGGER trg_audit_log_append_only
                BEFORE UPDATE OR DELETE ON audit_log
                FOR EACH ROW
                EXECUTE FUNCTION audit_log_append_only()
        """))
        await session.commit()


class TestAuditContext:
    async def test_audit_context_from_current_user(self):
        from app.core.audit_context import get_audit_context
        from fastapi import Request

        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)

            scope = {
                "type": "http",
                "method": "GET",
                "path": "/test",
                "headers": [
                    (b"user-agent", b"Chrome"),
                ],
                "client": ("1.2.3.4", 12345),
            }
            request = Request(scope)
            request.state.impersonation = False

            from app.schemas.auth import CurrentUser
            cu = CurrentUser(
                id=user.id,
                tenant_id=TENANT_ID,
                email=user.email,
                roles=[],
                permissions=frozenset(),
                is_active=True,
            )
            ctx = await get_audit_context(request=request, current_user=cu)
            assert ctx.actor_id == user.id
            assert ctx.tenant_id == TENANT_ID
            assert ctx.ip == "1.2.3.4"
            assert ctx.user_agent == "Chrome"
            assert ctx.impersonated_user_id is None
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_audit_context_with_impersonation(self):
        from app.core.audit_context import get_audit_context
        from fastapi import Request

        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            impersonated_id = uuid.uuid4()

            scope = {
                "type": "http",
                "method": "GET",
                "path": "/test",
                "headers": [],
            }
            request = Request(scope)
            request.state.impersonation = True
            request.state.impersonating_user_id = str(user.id)

            from app.schemas.auth import CurrentUser
            cu = CurrentUser(
                id=impersonated_id,
                tenant_id=TENANT_ID,
                email="impersonated@test.com",
                roles=[],
                permissions=frozenset(),
                is_active=True,
            )
            ctx = await get_audit_context(request=request, current_user=cu)
            assert ctx.actor_id == user.id
            assert ctx.impersonated_user_id == impersonated_id
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_audit_context_fallback_when_no_request_state(self):
        from app.core.audit_context import get_audit_context
        from fastapi import Request

        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)

            scope = {
                "type": "http",
                "method": "GET",
                "path": "/test",
                "headers": [],
            }
            request = Request(scope)

            from app.schemas.auth import CurrentUser
            cu = CurrentUser(
                id=user.id,
                tenant_id=TENANT_ID,
                email=user.email,
                roles=[],
                permissions=frozenset(),
                is_active=True,
            )
            ctx = await get_audit_context(request=request, current_user=cu)
            assert ctx.actor_id == user.id
            assert ctx.impersonated_user_id is None
        finally:
            await _teardown_db()
            await eng.dispose()


class TestAuditService:
    async def test_log_creates_entry(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            materia = await _seed_materia(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                service = AuditService(db=session, tenant_id=TENANT_ID)
                entry = await service.log(
                    accion=AuditActionCode.PADRON_CARGAR,
                    actor_id=user.id,
                    tenant_id=TENANT_ID,
                    materia_id=materia.id,
                    filas_afectadas=15,
                    detalle={"source": "moodle"},
                    ip="10.0.0.1",
                    user_agent="curl",
                )
                assert entry.id is not None
                assert entry.accion == "PADRON_CARGAR"
                assert entry.filas_afectadas == 15
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_log_with_impersonated_user(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            impersonated_id = uuid.uuid4()
            # Need to create the impersonated user in DB due to FK constraint
            factory_imp = async_sessionmaker(eng, expire_on_commit=False)
            async with factory_imp() as s:
                from app.core.security import hash_password
                imp_user = Usuario(
                    id=impersonated_id,
                    tenant_id=TENANT_ID,
                    email="impersonated@test.com",
                    hashed_password=hash_password("testpass"),
                    is_active=True,
                )
                s.add(imp_user)
                await s.commit()

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                service = AuditService(db=session, tenant_id=TENANT_ID)
                entry = await service.log(
                    accion=AuditActionCode.IMPERSONACION_INICIAR,
                    actor_id=user.id,
                    tenant_id=TENANT_ID,
                    impersonado_id=impersonated_id,
                )
                assert entry.impersonado_id == impersonated_id
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_log_with_minimal_fields(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                service = AuditService(db=session, tenant_id=TENANT_ID)
                entry = await service.log(
                    accion="TEST_MINIMAL",
                    actor_id=user.id,
                    tenant_id=TENANT_ID,
                )
                assert entry.accion == "TEST_MINIMAL"
                assert entry.filas_afectadas == 0
                assert entry.detalle is None
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_log_with_detalle_as_dict(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                service = AuditService(db=session, tenant_id=TENANT_ID)
                entry = await service.log(
                    accion="TEST_DETALLE",
                    actor_id=user.id,
                    tenant_id=TENANT_ID,
                    detalle={"key": "value", "nested": {"a": 1}},
                )
                assert entry.detalle == {"key": "value", "nested": {"a": 1}}
        finally:
            await _teardown_db()
            await eng.dispose()


# ===== Group 4: @audit_action Decorator =====


class TestAuditActionDecorator:
    async def test_decorator_logs_after_successful_execution(self):
        from app.core.audit_decorator import audit_action

        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                ctx = AuditContextCls(
                    actor_id=user.id,
                    impersonated_user_id=None,
                    ip="1.2.3.4",
                    user_agent="test",
                    tenant_id=TENANT_ID,
                )
                service = AuditService(db=session, tenant_id=TENANT_ID)

                class FakeService:
                    @audit_action("PADRON_CARGAR")
                    async def do_work(self, ctx, audit_service):
                        return {"filas_afectadas": 10}

                fsvc = FakeService()
                await fsvc.do_work(ctx, audit_service=service)
                await session.commit()

            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                items, total, pages = await repo.find(accion="PADRON_CARGAR")
                assert total == 1
                assert items[0].filas_afectadas == 10
                assert items[0].actor_id == user.id
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_decorator_captures_filas_afectadas_from_return(self):
        from app.core.audit_decorator import audit_action

        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                ctx = AuditContextCls(
                    actor_id=user.id,
                    impersonated_user_id=None,
                    ip=None,
                    user_agent=None,
                    tenant_id=TENANT_ID,
                )
                service = AuditService(db=session, tenant_id=TENANT_ID)

                class FakeService:
                    @audit_action("LIQUIDACION_CERRAR")
                    async def close(self, ctx, audit_service):
                        return {"filas_afectadas": 42, "liquidacion_id": "abc"}

                fsvc = FakeService()
                result = await fsvc.close(ctx, audit_service=service)
                await session.commit()
                assert result == {"filas_afectadas": 42, "liquidacion_id": "abc"}

            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                items, total, pages = await repo.find(accion="LIQUIDACION_CERRAR")
                assert items[0].filas_afectadas == 42
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_decorator_does_not_break_on_audit_failure(self):
        from app.core.audit_decorator import audit_action

        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                ctx = AuditContextCls(
                    actor_id=user.id,
                    impersonated_user_id=None,
                    ip=None,
                    user_agent=None,
                    tenant_id=TENANT_ID,
                )

                class BrokenService:
                    @audit_action("TEST")
                    async def work(self, ctx, audit_service):
                        return "success"

                bsvc = BrokenService()
                result = await bsvc.work(ctx, audit_service=None)
                assert result == "success"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_decorator_passes_through_exceptions(self):
        from app.core.audit_decorator import audit_action

        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                ctx = AuditContextCls(
                    actor_id=user.id,
                    impersonated_user_id=None,
                    ip=None,
                    user_agent=None,
                    tenant_id=TENANT_ID,
                )
                service = AuditService(db=session, tenant_id=TENANT_ID)

                class FailService:
                    @audit_action("FAIL")
                    async def fail(self, ctx, audit_service):
                        raise ValueError("operation failed")

                fsvc = FailService()
                with pytest.raises(ValueError, match="operation failed"):
                    await fsvc.fail(ctx, audit_service=service)

            async with factory() as session:
                repo = AuditLogRepository(session, TENANT_ID)
                items, total, pages = await repo.find(accion="FAIL")
                assert total == 0
        finally:
            await _teardown_db()
            await eng.dispose()


# ===== Group 6: Audit Log API Endpoint =====


async def _seed_audit_log(
    eng, actor_id: uuid.UUID, accion: str = "PADRON_CARGAR",
    materia_id: uuid.UUID | None = None,
    filas_afectadas: int = 0,
    days_offset: int = 0,
) -> uuid.UUID:
    from app.models.audit_log import AuditLog
    from datetime import datetime, timedelta, timezone
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        entry = AuditLog(
            id=uuid.uuid4(),
            tenant_id=TENANT_ID,
            actor_id=actor_id,
            accion=accion,
            materia_id=materia_id,
            filas_afectadas=filas_afectadas,
            fecha_hora=datetime.now(timezone.utc) - timedelta(days=days_offset),
        )
        session.add(entry)
        await session.commit()
        return entry.id


class TestAuditLogApi:
    async def test_list_audit_log_requires_permission(self):
        from httpx import ASGITransport, AsyncClient
        from app.main import create_app
        from app.core.security import create_access_token

        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)

            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": [],
            })

            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.get(
                    "/api/audit/log",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_list_audit_log_returns_paginated_results(self):
        from httpx import ASGITransport, AsyncClient
        from app.main import create_app
        from app.core.security import create_access_token

        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role_id = await _seed_role_with_permission(eng, "ADMIN", "auditoria:ver")
            await _assign_role(eng, user.id, role_id)
            for i in range(5):
                await _seed_audit_log(eng, user.id, f"ACCION_{i}")

            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": ["ADMIN"],
            })

            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.get(
                    "/api/audit/log",
                    params={"limit": 2, "offset": 0},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert len(data["items"]) == 2
            assert data["total"] == 5
            assert data["pages"] == 3
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_list_audit_log_filters_by_accion(self):
        from httpx import ASGITransport, AsyncClient
        from app.main import create_app
        from app.core.security import create_access_token

        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role_id = await _seed_role_with_permission(eng, "ADMIN", "auditoria:ver")
            await _assign_role(eng, user.id, role_id)
            await _seed_audit_log(eng, user.id, "PADRON_CARGAR")
            await _seed_audit_log(eng, user.id, "LIQUIDACION_CERRAR")

            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": ["ADMIN"],
            })

            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.get(
                    "/api/audit/log",
                    params={"accion": "LIQUIDACION_CERRAR"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert len(data["items"]) == 1
            assert data["items"][0]["accion"] == "LIQUIDACION_CERRAR"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_list_audit_log_tenant_isolation(self):
        from httpx import ASGITransport, AsyncClient
        from app.main import create_app
        from app.core.security import create_access_token

        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role_id = await _seed_role_with_permission(eng, "ADMIN", "auditoria:ver")
            await _assign_role(eng, user.id, role_id)
            await _seed_audit_log(eng, user.id, "PADRON_CARGAR")

            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": ["ADMIN"],
            })

            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.get(
                    "/api/audit/log",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            for item in data["items"]:
                assert item["tenant_id"] == str(TENANT_ID)
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_list_audit_log_returns_audit_log_response_shape(self):
        from httpx import ASGITransport, AsyncClient
        from app.main import create_app
        from app.core.security import create_access_token

        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role_id = await _seed_role_with_permission(eng, "ADMIN", "auditoria:ver")
            await _assign_role(eng, user.id, role_id)
            await _seed_audit_log(eng, user.id, "PADRON_CARGAR")

            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": ["ADMIN"],
            })

            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.get(
                    "/api/audit/log",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert "total" in data
            assert "pages" in data
            assert "limit" in data
            assert "offset" in data
            assert len(data["items"]) >= 1
        finally:
            await _teardown_db()
            await eng.dispose()


# ===== Group 7: Permission Seed Update =====


class TestAuditPermissions:
    async def test_auditoria_ver_seeded_in_admin_role(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            from app.models.role import Role

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                role = Role(
                    id=uuid.uuid4(),
                    tenant_id=TENANT_ID,
                    name="ADMIN",
                    permissions=["auditoria:ver", "impersonacion:usar"],
                    is_system_role=True,
                )
                session.add(role)
                await session.commit()

            async with factory() as session:
                from sqlalchemy import select
                result = await session.execute(
                    select(Role).where(Role.name == "ADMIN", Role.tenant_id == TENANT_ID)
                )
                admin_role = result.scalars().first()
                assert admin_role is not None
                assert "auditoria:ver" in admin_role.permissions
                assert "impersonacion:usar" in admin_role.permissions
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_auditoria_ver_not_seeded_in_roles_without_permission(self):
        """Roles other than COORDINADOR/ADMIN/FINANZAS should not get auditoria:ver."""
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            from app.models.role import Role

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                role = Role(
                    id=uuid.uuid4(),
                    tenant_id=TENANT_ID,
                    name="TUTOR",
                    permissions=[],
                    is_system_role=True,
                )
                session.add(role)
                await session.commit()

            async with factory() as session:
                from sqlalchemy import select
                result = await session.execute(
                    select(Role).where(Role.name == "TUTOR", Role.tenant_id == TENANT_ID)
                )
                tutor_role = result.scalars().first()
                assert "auditoria:ver" not in tutor_role.permissions
        finally:
            await _teardown_db()
            await eng.dispose()


# ===== Group 8: Module Wiring (e2e) =====


class TestEndToEnd:
    async def test_e2e_action_logged_via_endpoint_and_visible_via_api(self):
        from httpx import ASGITransport, AsyncClient
        from app.main import create_app
        from app.core.security import create_access_token

        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            target = await _seed_user(eng)
            role_id = await _seed_role_with_permission(eng, "ADMIN", "impersonacion:usar")
            await _assign_role(eng, user.id, role_id)
            audit_role_id = await _seed_role_with_permission(eng, "AUDITOR", "auditoria:ver")
            await _assign_role(eng, user.id, audit_role_id)

            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": ["ADMIN"],
            })

            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                start_resp = await client.post(
                    "/api/auth/impersonate/start",
                    json={"user_id": str(target.id)},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert start_resp.status_code == 200

            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                audit_resp = await client.get(
                    "/api/audit/log",
                    params={"accion": "IMPERSONACION_INICIAR"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert audit_resp.status_code == 200
            data = audit_resp.json()
            assert len(data["items"]) >= 1
            assert data["items"][0]["accion"] == "IMPERSONACION_INICIAR"
        finally:
            await _teardown_db()
            await eng.dispose()


async def _seed_role_with_permission(eng, name: str, permission: str) -> uuid.UUID:
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


async def _assign_role(eng, usuario_id: uuid.UUID, role_id: uuid.UUID):
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


class TestImpersonationToken:
    async def test_create_impersonation_token_produces_valid_jwt(self):
        from app.core.security import create_impersonation_token, decode_token
        actor_id = uuid.uuid4()
        target_id = uuid.uuid4()
        token = create_impersonation_token(
            impersonating_user_id=actor_id,
            target_user_id=target_id,
            tenant_id=TENANT_ID,
        )
        payload = decode_token(token)
        assert payload["sub"] == str(target_id)
        assert payload["impersonating_user_id"] == str(actor_id)
        assert payload["impersonation"] is True
        assert payload["tenant_id"] == str(TENANT_ID)
        assert payload["exp"] is not None

    async def test_impersonation_token_expiration(self):
        from app.core.security import create_impersonation_token, decode_token
        actor_id = uuid.uuid4()
        target_id = uuid.uuid4()
        token = create_impersonation_token(
            impersonating_user_id=actor_id,
            target_user_id=target_id,
            tenant_id=TENANT_ID,
            expire_minutes=1,
        )
        payload = decode_token(token)
        exp = payload["exp"]
        assert isinstance(exp, int)


class TestImpersonationApi:
    async def test_impersonate_start_returns_impersonation_token(self):
        from httpx import ASGITransport, AsyncClient
        from app.main import create_app
        from app.core.security import create_access_token

        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            target = await _seed_user(eng)
            role_id = await _seed_role_with_permission(eng, "ADMIN", "impersonacion:usar")
            await _assign_role(eng, user.id, role_id)

            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": ["ADMIN"],
            })

            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.post(
                    "/api/auth/impersonate/start",
                    json={"user_id": str(target.id)},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            assert data["impersonating_user_id"] == str(user.id)
            assert data["target_user_id"] == str(target.id)
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_impersonate_start_creates_audit_log(self):
        from httpx import ASGITransport, AsyncClient
        from app.main import create_app
        from app.core.security import create_access_token

        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            target = await _seed_user(eng)
            role_id = await _seed_role_with_permission(eng, "ADMIN", "impersonacion:usar")
            await _assign_role(eng, user.id, role_id)

            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": ["ADMIN"],
            })

            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                await client.post(
                    "/api/auth/impersonate/start",
                    json={"user_id": str(target.id)},
                    headers={"Authorization": f"Bearer {token}"},
                )

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.repositories.audit_log_repository import AuditLogRepository
                repo = AuditLogRepository(session, TENANT_ID)
                items, total, pages = await repo.find(accion="IMPERSONACION_INICIAR")
                assert total >= 1
                assert items[0].impersonado_id == target.id
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_impersonate_without_permission_returns_403(self):
        from httpx import ASGITransport, AsyncClient
        from app.main import create_app
        from app.core.security import create_access_token

        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            target = await _seed_user(eng)

            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": [],
            })

            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.post(
                    "/api/auth/impersonate/start",
                    json={"user_id": str(target.id)},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_impersonate_end_logs_audit(self):
        from httpx import ASGITransport, AsyncClient
        from app.main import create_app
        from app.core.security import create_access_token

        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role_id = await _seed_role_with_permission(eng, "ADMIN", "impersonacion:usar")
            await _assign_role(eng, user.id, role_id)

            token = create_access_token({
                "sub": str(user.id),
                "tenant_id": str(TENANT_ID),
                "roles": ["ADMIN"],
            })

            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                response = await client.post(
                    "/api/auth/impersonate/end",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.repositories.audit_log_repository import AuditLogRepository
                repo = AuditLogRepository(session, TENANT_ID)
                items, total, pages = await repo.find(accion="IMPERSONACION_FINALIZAR")
                assert total >= 1
        finally:
            await _teardown_db()
            await eng.dispose()
