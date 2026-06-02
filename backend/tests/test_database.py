import pytest
from sqlalchemy import text

from app.core.database import get_factory
from app.core.dependencies import get_db


class TestDatabaseConnection:
    async def test_select_one(self, db_session):
        result = await db_session.execute(text("SELECT 1 AS value"))
        row = result.one()
        assert row.value == 1

    async def test_session_closes_on_exception(self):
        gen = get_db()
        session = await gen.__anext__()
        assert session.is_active
        with pytest.raises(RuntimeError):
            await gen.athrow(RuntimeError("boom"))
        # Verify pool is not leaking: a new session can still acquire a connection
        new_session = get_factory()()
        try:
            result = await new_session.execute(text("SELECT 1 AS value"))
            row = result.one()
            assert row.value == 1
        finally:
            await new_session.close()
        from app.core.database import close_db_engine
        await close_db_engine()
