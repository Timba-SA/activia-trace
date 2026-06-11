"""Check actual DB state."""
import asyncio
from app.core.database import get_factory
from sqlalchemy import text

async def check():
    factory = get_factory()
    async with factory() as session:
        # Check alembic version
        result = await session.execute(text("SELECT version_num FROM alembic_version"))
        print(f"alembic_version: {result.scalar()}")

        # Check usuario columns
        result = await session.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name='usuario' ORDER BY ordinal_position")
        )
        cols = [r[0] for r in result]
        print(f"usuario columns ({len(cols)}): {cols}")

        # Check tenant columns
        result = await session.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name='tenant' ORDER BY ordinal_position")
        )
        cols = [r[0] for r in result]
        print(f"tenant columns ({len(cols)}): {cols}")

        # Check role columns
        result = await session.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name='role' ORDER BY ordinal_position")
        )
        cols = [r[0] for r in result]
        print(f"role columns ({len(cols)}): {cols}")

        # Check if tenant exists
        result = await session.execute(text("SELECT id, name, slug FROM tenant"))
        for r in result:
            print(f"Tenant: {r}")

        # Check if role exists
        result = await session.execute(text("SELECT id, name FROM role"))
        for r in result:
            print(f"Role: {r}")

asyncio.run(check())
