from app.main import create_app


class TestAppStartup:
    async def test_app_creates_without_error(self):
        app = create_app()
        assert app.title == "active-trace"
        assert app.version == "0.1.0"

    async def test_app_has_health_route(self):
        app = create_app()
        routes = [r.path for r in app.routes]
        assert "/health" in routes
