"""Check DB schema for key tables."""
import asyncio
from sqlalchemy import text
from app.core.database import get_factory


async def get():
    factory = get_factory()
    async with factory() as s:
        tables = ['slot_encuentro', 'guardia', 'instancia_encuentro']
        for table in tables:
            print(f"\n=== {table} ===")
            r = await s.execute(
                text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name='{table}' ORDER BY ordinal_position")
            )
            for row in r:
                print(f"  {row[0]}: {row[1]}")


asyncio.run(get())
