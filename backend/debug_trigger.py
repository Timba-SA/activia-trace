"""Debug script to verify the PostgreSQL append-only trigger."""
import asyncio
import uuid
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.database import Base
from app.core.security import hash_password
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.models.audit_log import AuditLog

DB_URL = "postgresql+asyncpg://active_trace:active_trace@localhost:5432/active_trace_test"


async def main():
    tid = uuid.UUID("00000000-0000-0000-0000-000000000001")
    eng = create_async_engine(DB_URL, echo=True)

    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Check if trigger already exists
        r = await conn.execute(
            sa.text("SELECT tgname FROM pg_trigger WHERE tgname = 'trg_audit_log_append_only'")
        )
        print(f"Trigger exists before install: {r.scalar()}")

        # Install trigger
        await conn.execute(
            sa.text(
                "CREATE OR REPLACE FUNCTION reject_audit_log_modification() "
                "RETURNS TRIGGER AS $$ "
                "BEGIN RAISE EXCEPTION 'audit_log is append-only: UPDATE and DELETE are not permitted'; "
                "END; $$ LANGUAGE plpgsql;"
            )
        )
        await conn.execute(
            sa.text(
                "CREATE TRIGGER trg_audit_log_append_only "
                "BEFORE UPDATE OR DELETE ON audit_log "
                "FOR EACH ROW EXECUTE FUNCTION reject_audit_log_modification();"
            )
        )

        # Verify trigger exists
        r = await conn.execute(
            sa.text("SELECT tgname FROM pg_trigger WHERE tgname = 'trg_audit_log_append_only'")
        )
        print(f"Trigger exists after install: {r.scalar()}")

        # Seed data
        tenant = Tenant(id=tid, name="T", slug="t", code="T")
        conn.session.add(tenant)
        user = Usuario(id=uuid.uuid4(), tenant_id=tid, email="test@t.com", hashed_password=hash_password("x"))
        conn.session.add(user)
        await conn.session.flush()

        log = AuditLog(tenant_id=tid, actor_id=user.id, accion="TEST")
        conn.session.add(log)
        await conn.session.flush()
        log_id = log.id

        # Try UPDATE via raw SQL
        try:
            await conn.execute(
                sa.text("UPDATE audit_log SET accion = 'CHANGED' WHERE id = :id"),
                {"id": log_id},
            )
            print("RAW SQL UPDATE succeeded (BAD!)")
        except Exception as e:
            print(f"RAW SQL UPDATE rejected: {e}")

        # Try UPDATE via SQLAlchemy ORM
        try:
            stmt = sa.update(AuditLog).where(AuditLog.id == log_id).values(accion="CHANGED")
            await conn.execute(stmt)
            print("ORM UPDATE succeeded (BAD!)")
        except Exception as e:
            print(f"ORM UPDATE rejected: {e}")

    await eng.dispose()


asyncio.run(main())
