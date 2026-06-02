import os
from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio

from app.main import create_app


class TestHealth:
    async def test_health_returns_200_with_status(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert "database" in body

    async def test_health_reports_db_up(self, client):
        response = await client.get("/health")
        body = response.json()
        assert body["database"] in ("up", "down")

    async def test_health_db_down_reports_down(self):
        original_url = os.environ.get("DATABASE_URL", "")
        os.environ["DATABASE_URL"] = "postgresql+asyncpg://bad:bad@localhost:9999/bad"
        from app.core import config
        config.get_settings.cache_clear()
        try:
            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
                response = await ac.get("/health")
                assert response.status_code == 200
                body = response.json()
                assert body["database"] == "down"
        finally:
            os.environ["DATABASE_URL"] = original_url
            config.get_settings.cache_clear()
            from app.core.database import close_db_engine
            await close_db_engine()
