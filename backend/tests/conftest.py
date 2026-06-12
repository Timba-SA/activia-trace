import os
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

_db_host = os.environ.get("POSTGRES_HOST", "localhost")
os.environ.setdefault("DATABASE_URL", f"postgresql+asyncpg://active_trace:active_trace@{_db_host}:5432/active_trace_test")
os.environ.setdefault("SECRET_KEY", "abcd1234abcd1234abcd1234abcd1234")
os.environ.setdefault("ENCRYPTION_KEY", "abcd1234abcd1234abcd1234abcd1234")

from app.core.database import Base


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(os.environ["DATABASE_URL"], echo=False)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session = factory()
    try:
        yield session
    finally:
        await session.rollback()
        await session.close()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest_asyncio.fixture
async def api_db() -> AsyncGenerator[AsyncSession, None]:
    """DB session that commits — for use with API tests where data must be visible to get_db()."""
    engine = create_async_engine(os.environ["DATABASE_URL"], echo=False)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session = factory()
    try:
        yield session
        await session.commit()
    finally:
        await session.close()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    from app.core.database import close_db_engine
    from app.main import create_app
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
    await close_db_engine()
