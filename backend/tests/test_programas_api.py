"""Integration tests for programas and fechas academicas endpoints."""
import os
import uuid
from datetime import date, time

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base, close_db_engine
from app.core.security import create_access_token, hash_password
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.fecha_academica import FechaAcademica
from app.models.materia import Materia
from app.models.programa_materia import ProgramaMateria
from app.models.role import Role
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.models.usuario_role import UsuarioRole

pytestmark = pytest.mark.asyncio

_db_host = os.environ.get('POSTGRES_HOST', 'localhost')
DB_URL = f"postgresql+asyncpg://active_trace:active_trace@{_db_host}:5432/active_trace_test"
TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


async def _setup_db():
    eng = create_async_engine(DB_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await eng.dispose()


async def _teardown_db():
    eng = create_async_engine(DB_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()
    await close_db_engine()


async def _seed_tenant(eng, tenant_id=TENANT_ID, slug="test-tenant"):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        tenant = Tenant(id=tenant_id, name="Test", slug=slug, code="TEST")
        session.add(tenant)
        await session.commit()


async def _seed_user(eng, tenant_id=TENANT_ID, email="user@test.com", password="testpass123"):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        user = Usuario(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            email=email,
            hashed_password=hash_password(password),
            is_active=True,
        )
        session.add(user)
        await session.commit()
        return user


async def _seed_role(eng, tenant_id=TENANT_ID, name="COORDINADOR", permissions=None):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        role = Role(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name=name,
            permissions=permissions or [],
            is_system_role=True,
        )
        session.add(role)
        await session.commit()
        return role


async def _assign_role(eng, user_id, role_id, tenant_id=TENANT_ID):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        session.add(UsuarioRole(usuario_id=user_id, role_id=role_id, tenant_id=tenant_id))
        await session.commit()


async def _make_app():
    from app.main import create_app
    app = create_app()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


async def _seed_carrera(eng, tenant_id=TENANT_ID):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        carrera = Carrera(id=uuid.uuid4(), tenant_id=tenant_id, nombre="Licenciatura Test", codigo="LT")
        session.add(carrera)
        await session.commit()
        return carrera


async def _seed_materia(eng, tenant_id=TENANT_ID, carrera_id=None):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        materia = Materia(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            nombre="Matematica Test",
            codigo="MT",
            carrera_id=carrera_id,
        )
        session.add(materia)
        await session.commit()
        return materia


async def _seed_cohorte(eng, tenant_id=TENANT_ID, carrera_id=None):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        cohorte = Cohorte(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            carrera_id=carrera_id,
            nombre="2025",
            anio=2025,
        )
        session.add(cohorte)
        await session.commit()
        return cohorte


async def _seed_programa(
    eng,
    tenant_id=TENANT_ID,
    materia_id=None,
    carrera_id=None,
    cohorte_id=None,
    titulo="Programa Test",
    version=1,
    activo=True,
):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        programa = ProgramaMateria(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            titulo=titulo,
            version=version,
            activo=activo,
        )
        session.add(programa)
        await session.commit()
        return programa


async def _seed_fecha(
    eng,
    tenant_id=TENANT_ID,
    materia_id=None,
    cohorte_id=None,
    tipo="Parcial",
    fecha=date(2025, 6, 15),
    numero=1,
):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        fa = FechaAcademica(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            tipo=tipo,
            numero=numero,
            fecha=fecha,
        )
        session.add(fa)
        await session.commit()
        return fa


# ─── 7.1 Repository: ProgramaMateriaRepository ──────────────────────────────

class TestProgramaMateriaRepository:
    async def test_create_programa(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.repositories.programa_materia_repository import ProgramaMateriaRepository
                repo = ProgramaMateriaRepository(session, TENANT_ID)
                programa = await repo.create(
                    tenant_id=TENANT_ID,
                    materia_id=materia.id,
                    carrera_id=carrera.id,
                    cohorte_id=cohorte.id,
                    titulo="Programa de Matematica",
                    version=1,
                    activo=True,
                )
                assert programa.id is not None
                assert programa.titulo == "Programa de Matematica"
                assert programa.version == 1
                assert programa.activo is True
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_get_programa(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            prog = await _seed_programa(eng, materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.repositories.programa_materia_repository import ProgramaMateriaRepository
                repo = ProgramaMateriaRepository(session, TENANT_ID)
                found = await repo.get(prog.id)
                assert found.id == prog.id
                assert found.titulo == "Programa Test"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_get_programa_not_found(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.repositories.programa_materia_repository import ProgramaMateriaRepository
                from app.core.exceptions import NotFoundError
                repo = ProgramaMateriaRepository(session, TENANT_ID)
                with pytest.raises(NotFoundError):
                    await repo.get(uuid.uuid4())
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_update_programa(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            prog = await _seed_programa(eng, materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.repositories.programa_materia_repository import ProgramaMateriaRepository
                repo = ProgramaMateriaRepository(session, TENANT_ID)
                updated = await repo.update(prog.id, titulo="Nuevo titulo")
                assert updated.titulo == "Nuevo titulo"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_list_with_filters(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia1 = await _seed_materia(eng, carrera_id=carrera.id)
            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                materia2 = Materia(
                    id=uuid.uuid4(), tenant_id=TENANT_ID, nombre="Fisica Test",
                    codigo="FT", carrera_id=carrera.id,
                )
                session.add(materia2)
                await session.commit()

            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            await _seed_programa(eng, materia_id=materia1.id, carrera_id=carrera.id, cohorte_id=cohorte.id, titulo="Prog 1")
            await _seed_programa(eng, materia_id=materia2.id, carrera_id=carrera.id, cohorte_id=cohorte.id, titulo="Prog 2")

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.repositories.programa_materia_repository import ProgramaMateriaRepository
                repo = ProgramaMateriaRepository(session, TENANT_ID)
                items, total, pages = await repo.list_filters(
                    materia_id=materia1.id, limit=20, offset=0
                )
                assert total == 1
                assert items[0].titulo == "Prog 1"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_get_active_for_materia_carrera_cohorte(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            await _seed_programa(eng, materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
                                 titulo="Activo", activo=True)
            await _seed_programa(eng, materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
                                 titulo="Inactivo", version=2, activo=False)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.repositories.programa_materia_repository import ProgramaMateriaRepository
                repo = ProgramaMateriaRepository(session, TENANT_ID)
                active = await repo.get_active_for_materia_carrera_cohorte(materia.id, carrera.id, cohorte.id)
                assert active is not None
                assert active.titulo == "Activo"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_get_max_version(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            await _seed_programa(eng, materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
                                 titulo="v1", version=1)
            await _seed_programa(eng, materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
                                 titulo="v2", version=2)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.repositories.programa_materia_repository import ProgramaMateriaRepository
                repo = ProgramaMateriaRepository(session, TENANT_ID)
                max_ver = await repo.get_max_version(materia.id, carrera.id, cohorte.id)
                assert max_ver == 2
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_get_max_version_no_programas(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.repositories.programa_materia_repository import ProgramaMateriaRepository
                repo = ProgramaMateriaRepository(session, TENANT_ID)
                max_ver = await repo.get_max_version(materia.id, carrera.id, cohorte.id)
                assert max_ver == 0
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_deactivate_all_for(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            p1 = await _seed_programa(eng, materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
                                      titulo="v1", version=1, activo=True)
            p1_id = p1.id

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                stmt = select(ProgramaMateria).where(ProgramaMateria.id == p1_id)
                result = await session.execute(stmt)
                before = result.scalars().first()
                assert before is not None
                assert before.activo is True

                from app.repositories.programa_materia_repository import ProgramaMateriaRepository
                repo = ProgramaMateriaRepository(session, TENANT_ID)
                await repo.deactivate_all_for(materia.id, carrera.id, cohorte.id)

                result = await session.execute(stmt)
                after = result.scalars().first()
                assert after is not None
                assert after.activo is False
        finally:
            await _teardown_db()
            await eng.dispose()


# ─── 7.2 Repository: FechaAcademicaRepository ─────────────────────────────

class TestFechaAcademicaRepository:
    async def test_create_fecha(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.repositories.fecha_academica_repository import FechaAcademicaRepository
                repo = FechaAcademicaRepository(session, TENANT_ID)
                fa = await repo.create(
                    tenant_id=TENANT_ID,
                    materia_id=materia.id,
                    cohorte_id=cohorte.id,
                    tipo="Parcial",
                    numero=1,
                    fecha=date(2025, 6, 15),
                )
                assert fa.id is not None
                assert fa.tipo == "Parcial"
                assert fa.fecha == date(2025, 6, 15)
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_get_fecha(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            fa = await _seed_fecha(eng, materia_id=materia.id, cohorte_id=cohorte.id)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.repositories.fecha_academica_repository import FechaAcademicaRepository
                repo = FechaAcademicaRepository(session, TENANT_ID)
                found = await repo.get(fa.id)
                assert found.id == fa.id
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_soft_delete_fecha(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            fa = await _seed_fecha(eng, materia_id=materia.id, cohorte_id=cohorte.id)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.repositories.fecha_academica_repository import FechaAcademicaRepository
                repo = FechaAcademicaRepository(session, TENANT_ID)
                await repo.soft_delete(fa.id)
                await session.commit()

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.repositories.fecha_academica_repository import FechaAcademicaRepository
                from app.core.exceptions import NotFoundError
                repo = FechaAcademicaRepository(session, TENANT_ID)
                with pytest.raises(NotFoundError):
                    await repo.get(fa.id)
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_list_fechas_with_filters(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            await _seed_fecha(eng, materia_id=materia.id, cohorte_id=cohorte.id, tipo="Parcial", numero=1)
            await _seed_fecha(eng, materia_id=materia.id, cohorte_id=cohorte.id, tipo="TP", numero=1)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.repositories.fecha_academica_repository import FechaAcademicaRepository
                repo = FechaAcademicaRepository(session, TENANT_ID)
                items, total, pages = await repo.list_filters(
                    tipo="Parcial", limit=20, offset=0
                )
                assert total == 1
                assert items[0].tipo == "Parcial"
        finally:
            await _teardown_db()
            await eng.dispose()


# ─── 7.3 Service: Programa versioning ────────────────────────────────────

class TestProgramaMateriaService:
    async def test_create_programa_version_1(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            user = await _seed_user(eng)
            from app.schemas.programa_materia import ProgramaMateriaCreate

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.services.programa_materia_service import ProgramaMateriaService
                service = ProgramaMateriaService(session, TENANT_ID, user.id)
                data = ProgramaMateriaCreate(
                    materia_id=materia.id,
                    carrera_id=carrera.id,
                    cohorte_id=cohorte.id,
                    titulo="Programa v1",
                )
                result = await service.create(data)
                assert result.version == 1
                assert result.activo is True
                assert result.titulo == "Programa v1"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_create_programa_auto_increment_version(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            user = await _seed_user(eng)
            from app.schemas.programa_materia import ProgramaMateriaCreate

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.services.programa_materia_service import ProgramaMateriaService
                service = ProgramaMateriaService(session, TENANT_ID, user.id)
                data1 = ProgramaMateriaCreate(
                    materia_id=materia.id,
                    carrera_id=carrera.id,
                    cohorte_id=cohorte.id,
                    titulo="v1",
                )
                r1 = await service.create(data1)
                assert r1.version == 1

                data2 = ProgramaMateriaCreate(
                    materia_id=materia.id,
                    carrera_id=carrera.id,
                    cohorte_id=cohorte.id,
                    titulo="v2",
                )
                r2 = await service.create(data2)
                assert r2.version == 2
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_create_programa_deactivates_previous(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            user = await _seed_user(eng)
            from app.schemas.programa_materia import ProgramaMateriaCreate

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.services.programa_materia_service import ProgramaMateriaService
                from app.repositories.programa_materia_repository import ProgramaMateriaRepository
                service = ProgramaMateriaService(session, TENANT_ID, user.id)
                repo = ProgramaMateriaRepository(session, TENANT_ID)

                data1 = ProgramaMateriaCreate(
                    materia_id=materia.id,
                    carrera_id=carrera.id,
                    cohorte_id=cohorte.id,
                    titulo="v1",
                )
                r1 = await service.create(data1)

                data2 = ProgramaMateriaCreate(
                    materia_id=materia.id,
                    carrera_id=carrera.id,
                    cohorte_id=cohorte.id,
                    titulo="v2",
                )
                r2 = await service.create(data2)

                old = await repo.get(r1.id, include_deleted=True)
                assert old.activo is False
                assert r2.activo is True
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_update_programa(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            user = await _seed_user(eng)
            from app.schemas.programa_materia import ProgramaMateriaUpdate

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.services.programa_materia_service import ProgramaMateriaService
                service = ProgramaMateriaService(session, TENANT_ID, user.id)

                data = ProgramaMateriaUpdate(titulo="Actualizado")
                from app.repositories.programa_materia_repository import ProgramaMateriaRepository
                repo = ProgramaMateriaRepository(session, TENANT_ID)
                prog = await repo.create(
                    tenant_id=TENANT_ID, materia_id=materia.id, carrera_id=carrera.id,
                    cohorte_id=cohorte.id, titulo="Original", version=1, activo=True,
                )
                updated = await service.update(prog.id, data)
                assert updated.titulo == "Actualizado"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_list_programas(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            user = await _seed_user(eng)
            await _seed_programa(eng, materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id, titulo="A")
            await _seed_programa(eng, materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
                                 titulo="B", version=2)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.services.programa_materia_service import ProgramaMateriaService
                service = ProgramaMateriaService(session, TENANT_ID, user.id)
                items, total, pages = await service.list({}, limit=20, offset=0)
                assert total == 2
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_deactivate_programa(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            user = await _seed_user(eng)
            prog = await _seed_programa(eng, materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.services.programa_materia_service import ProgramaMateriaService
                service = ProgramaMateriaService(session, TENANT_ID, user.id)
                await service.deactivate(prog.id)
                await session.commit()

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.repositories.programa_materia_repository import ProgramaMateriaRepository
                repo = ProgramaMateriaRepository(session, TENANT_ID)
                old = await repo.get(prog.id, include_deleted=True)
                assert old.activo is False
        finally:
            await _teardown_db()
            await eng.dispose()


# ─── 7.4 Service: generar_contenido ──────────────────────────────────────

class TestGenerarContenido:
    async def test_generar_contenido_active_programa(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id, )
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            user = await _seed_user(eng)
            prog = await _seed_programa(eng, materia_id=materia.id, carrera_id=carrera.id,
                                        cohorte_id=cohorte.id, titulo="Programa Activo", activo=True)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.services.programa_materia_service import ProgramaMateriaService
                service = ProgramaMateriaService(session, TENANT_ID, user.id)
                result = await service.generar_contenido(prog.id)
                assert "Programa Activo" in result.contenido_html
                assert "<h2>" in result.contenido_html
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_generar_contenido_inactive_returns_404(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            user = await _seed_user(eng)
            prog = await _seed_programa(eng, materia_id=materia.id, carrera_id=carrera.id,
                                        cohorte_id=cohorte.id, titulo="Inactivo", activo=False)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.services.programa_materia_service import ProgramaMateriaService
                from fastapi import HTTPException
                service = ProgramaMateriaService(session, TENANT_ID, user.id)
                with pytest.raises(HTTPException) as exc:
                    await service.generar_contenido(prog.id)
                assert exc.value.status_code == 404
        finally:
            await _teardown_db()
            await eng.dispose()


# ─── 7.5 Service: FechasAcademica CRUD and soft delete ───────────────────

class TestFechaAcademicaService:
    async def test_create_fecha(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            user = await _seed_user(eng)
            from app.schemas.fecha_academica import FechaAcademicaCreate

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.services.fecha_academica_service import FechaAcademicaService
                service = FechaAcademicaService(session, TENANT_ID, user.id)
                data = FechaAcademicaCreate(
                    materia_id=materia.id,
                    cohorte_id=cohorte.id,
                    tipo="Parcial",
                    fecha=date(2025, 6, 15),
                    numero=1,
                )
                result = await service.create(data)
                assert result.tipo == "Parcial"
                assert result.fecha == date(2025, 6, 15)
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_update_fecha(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            user = await _seed_user(eng)
            fa = await _seed_fecha(eng, materia_id=materia.id, cohorte_id=cohorte.id)
            from app.schemas.fecha_academica import FechaAcademicaUpdate

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.services.fecha_academica_service import FechaAcademicaService
                service = FechaAcademicaService(session, TENANT_ID, user.id)
                data = FechaAcademicaUpdate(aula="Aula 101")
                result = await service.update(fa.id, data)
                assert result.aula == "Aula 101"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_soft_delete_fecha(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            user = await _seed_user(eng)
            fa = await _seed_fecha(eng, materia_id=materia.id, cohorte_id=cohorte.id)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.services.fecha_academica_service import FechaAcademicaService
                service = FechaAcademicaService(session, TENANT_ID, user.id)
                await service.delete(fa.id)
                await session.commit()

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.repositories.fecha_academica_repository import FechaAcademicaRepository
                from app.core.exceptions import NotFoundError
                repo = FechaAcademicaRepository(session, TENANT_ID)
                with pytest.raises(NotFoundError):
                    await repo.get(fa.id)
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_list_fechas(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            user = await _seed_user(eng)
            await _seed_fecha(eng, materia_id=materia.id, cohorte_id=cohorte.id, tipo="Parcial", numero=1)
            await _seed_fecha(eng, materia_id=materia.id, cohorte_id=cohorte.id, tipo="TP", numero=1)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.services.fecha_academica_service import FechaAcademicaService
                service = FechaAcademicaService(session, TENANT_ID, user.id)
                items, total, pages = await service.list({"tipo": "TP"}, limit=20, offset=0)
                assert total == 1
                assert items[0].tipo == "TP"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_get_fecha_by_id(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            user = await _seed_user(eng)
            fa = await _seed_fecha(eng, materia_id=materia.id, cohorte_id=cohorte.id)

            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from app.services.fecha_academica_service import FechaAcademicaService
                service = FechaAcademicaService(session, TENANT_ID, user.id)
                result = await service.get_by_id(fa.id)
                assert result.id == fa.id
        finally:
            await _teardown_db()
            await eng.dispose()


# ─── 7.6 Router: permissions, validation ─────────────────────────────────

class TestProgramasRouter:
    async def test_list_programas_requires_programas_ver(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["programas:ver"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            async with await _make_app() as client:
                response = await client.get(
                    "/api/programas/",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_create_programa_requires_programas_gestionar(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng, name="ALUMNO", permissions=[])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ALUMNO"]},
            )
            async with await _make_app() as client:
                response = await client.post(
                    "/api/programas/",
                    json={"materia_id": str(uuid.uuid4()), "carrera_id": str(uuid.uuid4()), "titulo": "Test"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_create_programa_422_invalid_data(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["programas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            async with await _make_app() as client:
                response = await client.post(
                    "/api/programas/",
                    json={"materia_id": "not-a-uuid", "carrera_id": str(uuid.uuid4()), "titulo": "Test"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 422
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_create_programa_creates_successfully(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["programas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            async with await _make_app() as client:
                response = await client.post(
                    "/api/programas/",
                    json={
                        "materia_id": str(materia.id),
                        "carrera_id": str(carrera.id),
                        "cohorte_id": str(cohorte.id),
                        "titulo": "Programa nuevo",
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 201
            data = response.json()
            assert data["titulo"] == "Programa nuevo"
            assert data["version"] == 1
            assert data["activo"] is True
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_get_programa_detail(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["programas:ver"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            prog = await _seed_programa(eng, materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id)
            async with await _make_app() as client:
                response = await client.get(
                    f"/api/programas/{prog.id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["id"] == str(prog.id)
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_delete_programa_deactivates(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["programas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            prog = await _seed_programa(eng, materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id)
            async with await _make_app() as client:
                response = await client.delete(
                    f"/api/programas/{prog.id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 204
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_generar_contenido_endpoint(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["programas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            prog = await _seed_programa(eng, materia_id=materia.id, carrera_id=carrera.id,
                                        cohorte_id=cohorte.id, titulo="Mi Programa", activo=True)
            async with await _make_app() as client:
                response = await client.post(
                    f"/api/programas/{prog.id}/generar-contenido",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert "Mi Programa" in data["contenido_html"]
        finally:
            await _teardown_db()
            await eng.dispose()


class TestFechasAcademicasRouter:
    async def test_create_fecha_requires_programas_gestionar(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng, name="ALUMNO", permissions=[])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["ALUMNO"]},
            )
            async with await _make_app() as client:
                response = await client.post(
                    "/api/fechas-academicas/",
                    json={
                        "materia_id": str(uuid.uuid4()),
                        "cohorte_id": str(uuid.uuid4()),
                        "tipo": "Parcial",
                        "fecha": "2025-06-15",
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_create_fecha_422_invalid_tipo(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["programas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            async with await _make_app() as client:
                response = await client.post(
                    "/api/fechas-academicas/",
                    json={
                        "materia_id": str(uuid.uuid4()),
                        "cohorte_id": str(uuid.uuid4()),
                        "tipo": "Invalido",
                        "fecha": "2025-06-15",
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 422
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_create_and_get_fecha(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["programas:gestionar", "programas:ver"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            async with await _make_app() as client:
                create_resp = await client.post(
                    "/api/fechas-academicas/",
                    json={
                        "materia_id": str(materia.id),
                        "cohorte_id": str(cohorte.id),
                        "tipo": "Parcial",
                        "numero": 1,
                        "fecha": "2025-06-15",
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert create_resp.status_code == 201
            fa_id = create_resp.json()["id"]

            async with await _make_app() as client:
                get_resp = await client.get(
                    f"/api/fechas-academicas/{fa_id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert get_resp.status_code == 200
            assert get_resp.json()["tipo"] == "Parcial"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_soft_delete_fecha_endpoint(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            carrera = await _seed_carrera(eng)
            materia = await _seed_materia(eng, carrera_id=carrera.id)
            cohorte = await _seed_cohorte(eng, carrera_id=carrera.id)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["programas:gestionar", "programas:ver"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            fa = await _seed_fecha(eng, materia_id=materia.id, cohorte_id=cohorte.id)
            async with await _make_app() as client:
                del_resp = await client.delete(
                    f"/api/fechas-academicas/{fa.id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert del_resp.status_code == 204

            async with await _make_app() as client:
                get_resp = await client.get(
                    f"/api/fechas-academicas/{fa.id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert get_resp.status_code == 404
        finally:
            await _teardown_db()
            await eng.dispose()
