from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.routers.analisis import router as analisis_router
from app.api.v1.routers.asignaciones import router as asignaciones_router
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.calificaciones import router as calificaciones_router
from app.api.v1.routers.carreras import router as carreras_router
from app.api.v1.routers.comunicaciones import router as comunicaciones_router
from app.api.v1.routers.cohortes import router as cohortes_router
from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.materias import router as materias_router
from app.api.v1.routers.padron import router as padron_router
from app.api.v1.routers.roles import router as roles_router
from app.api.v1.routers.user_roles import router as user_roles_router
from app.api.v1.routers.usuarios import router as usuarios_router
from app.core.database import close_db_engine
from app.core.logging import setup_logging
from app.core.observability import instrument_fastapi, setup_observability


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    setup_observability()
    yield
    await close_db_engine()


def create_app() -> FastAPI:
    app = FastAPI(
        title="active-trace",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(analisis_router)
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(roles_router)
    app.include_router(user_roles_router)
    app.include_router(asignaciones_router)
    app.include_router(calificaciones_router)
    app.include_router(carreras_router)
    app.include_router(cohortes_router)
    app.include_router(materias_router)
    app.include_router(padron_router)
    app.include_router(comunicaciones_router)
    app.include_router(usuarios_router)
    instrument_fastapi(app)
    return app


app = create_app()
