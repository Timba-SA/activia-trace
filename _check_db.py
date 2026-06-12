"""Check database tables and data."""
from sqlalchemy import text
from app.core.database import get_factory
import asyncio


async def get():
    factory = get_factory()
    async with factory() as s:
        # Get all tables
        r = await s.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
        )
        tables = [row[0] for row in r]
        print("=== TABLAS ===")
        for t in tables:
            print(f"  {t}")

        # Count rows in each table
        print("\n=== FILAS ===")
        for t in tables:
            try:
                r2 = await s.execute(text(f"SELECT count(*) FROM {t}"))
                cnt = r2.scalar()
                print(f"  {t}: {cnt}")
            except Exception as e:
                print(f"  {t}: ERROR - {e}")


asyncio.run(get())
