"""Check tenant table columns."""
import asyncio
from app.core.database import get_factory
from sqlalchemy import text

async def check():
    factory = get_factory()
    async with factory() as session:
        result = await session.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name='tenant' ORDER BY ordinal_position")
        )
        for row in result:
            print(row[0])

asyncio.run(check())
