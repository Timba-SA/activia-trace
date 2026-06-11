from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers.analisis import router as analisis_router
from app.api.v1.routers.audit import router as audit_router
from app.api.v1.routers.facturas import router as facturas_router
from app.api.v1.routers.liquidaciones import router as liquidaciones_router
from app.api.v1.routers.auditoria import router as auditoria_router
from app.api.v1.routers.asignaciones import router as asignaciones_router
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.avisos import router as avisos_router
from app.api.v1.routers.equipos import router as equipos_router
from app.api.v1.routers.inbox import router as inbox_router
from app.api.v1.routers.perfil import router as perfil_router
from app.api.v1.routers.programas import router as programas_router
from app.api.v1.routers.encuentros import router as encuentros_router
from app.api.v1.routers.evaluaciones import router as evaluaciones_router
from app.api.v1.routers.tareas import router as tareas_router
from app.api.v1.routers.guardias import router as guardias_router
from app.api.v1.routers.calificaciones import router as calificaciones_router
from app.api.v1.routers.fechas_academicas import router as fechas_academicas_router
from app.api.v1.routers.carreras import router as carreras_router
from app.api.v1.routers.comunicaciones import router as comunicaciones_router
from app.api.v1.routers.cohortes import router as cohortes_router
from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.materias import router as materias_router
from app.api.v1.routers.metricas import router as metricas_router
from app.api.v1.routers.padron import router as padron_router
from app.api.v1.routers.reservas import router as reservas_router
from app.api.v1.routers.resultados import router as resultados_router
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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(analisis_router)
    app.include_router(audit_router)
    app.include_router(facturas_router)
    app.include_router(liquidaciones_router)
    app.include_router(auditoria_router)
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(avisos_router)
    app.include_router(roles_router)
    app.include_router(user_roles_router)
    app.include_router(asignaciones_router)
    app.include_router(calificaciones_router)
    app.include_router(equipos_router)
    app.include_router(fechas_academicas_router)
    app.include_router(inbox_router)
    app.include_router(perfil_router)
    app.include_router(programas_router)
    app.include_router(encuentros_router)
    app.include_router(evaluaciones_router)
    app.include_router(guardias_router)
    app.include_router(carreras_router)
    app.include_router(cohortes_router)
    app.include_router(materias_router)
    app.include_router(metricas_router)
    app.include_router(padron_router)
    app.include_router(comunicaciones_router)
    app.include_router(reservas_router)
    app.include_router(tareas_router)
    app.include_router(resultados_router)
    app.include_router(usuarios_router)
    instrument_fastapi(app)
    return app


app = create_app()
