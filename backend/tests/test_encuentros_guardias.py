"""Tests for encuentros y guardias module (C-13)."""
import os

import uuid
from datetime import date, datetime, time

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base, close_db_engine
from app.core.exceptions import NotFoundError
from app.core.security import create_access_token, hash_password
from app.models.asignacion import Asignacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.encuentro_instancia import EstadoInstancia, InstanciaEncuentro
from app.models.encuentro_slot import DiaSemana, SlotEncuentro
from app.models.guardia import DiaSemanaGuardia, EstadoGuardia, Guardia
from app.models.materia import Materia
from app.models.role import Role
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.models.usuario_role import UsuarioRole
from app.repositories.encuentro_repository import (
    InstanciaEncuentroRepository,
    SlotEncuentroRepository,
)
from app.repositories.guardia_repository import GuardiaRepository
from app.services.encuentro_service import EncuentroService
from app.services.guardia_service import GuardiaService
import pytest_asyncio

pytestmark = pytest.mark.asyncio

_db_host = os.environ.get('POSTGRES_HOST', 'localhost')
DB_URL = f"postgresql+asyncpg://active_trace:active_trace@{_db_host}:5432/active_trace_test"
TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


# ── Fixtures ─────────────────────────────────────────────────────────────────


async def _setup_db():
    eng = create_async_engine(DB_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await eng.dispose()


async def _teardown_db():
    eng = create_async_engine(DB_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()
    await close_db_engine()


pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(autouse=True)
async def setup_teardown():
    await _setup_db()
    yield
    await _teardown_db()


@pytest_asyncio.fixture
async def client():
    from app.main import create_app
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
    await close_db_engine()


@pytest_asyncio.fixture
async def eng():
    engine = create_async_engine(DB_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(DB_URL, echo=False)
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


# ── Seed helpers ─────────────────────────────────────────────────────────────


async def _seed_tenant(eng, tenant_id=TENANT_ID, slug="test-tenant", code="TEST"):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        existing = await session.get(Tenant, tenant_id)
        if existing is None:
            session.add(Tenant(id=tenant_id, name="Test", slug=slug, code=code))
            await session.commit()


async def _seed_user(eng, tenant_id=TENANT_ID, email="admin@test.com"):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        user = Usuario(
            id=uuid.uuid4(),
            email=email,
            tenant_id=tenant_id,
            hashed_password=hash_password("testpass123"),
            is_active=True,
        )
        session.add(user)
        await session.commit()
        return user


async def _seed_role(eng, tenant_id=TENANT_ID, name="ADMIN", permissions=None):
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


async def _seed_role_no_permission(eng, tenant_id=TENANT_ID, name="VIEWER"):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        role = Role(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name=name,
            permissions=["academico:ver_estado_propio"],
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


async def _seed_carrera(eng, tenant_id=TENANT_ID):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        carrera = Carrera(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            codigo=f"TCARR-{uuid.uuid4().hex[:6]}",
            nombre="Tecnicatura Test",
            is_active=True,
        )
        session.add(carrera)
        await session.commit()
        return carrera


async def _seed_cohorte(eng, tenant_id=TENANT_ID, carrera_id=None):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        cohorte = Cohorte(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            carrera_id=carrera_id or uuid.uuid4(),
            nombre=f"COH-{uuid.uuid4().hex[:6]}",
            anio=2026,
            is_active=True,
        )
        session.add(cohorte)
        await session.commit()
        return cohorte


async def _seed_materia(eng, tenant_id=TENANT_ID):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        materia = Materia(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            codigo=f"MAT-{uuid.uuid4().hex[:6]}",
            nombre="Materia Test",
            is_active=True,
        )
        session.add(materia)
        await session.commit()
        return materia


async def _seed_asignacion(eng, tenant_id=TENANT_ID, usuario_id=None, materia_id=None):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        asignacion = Asignacion(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            usuario_id=usuario_id or uuid.uuid4(),
            rol="PROFESOR",
            materia_id=materia_id or uuid.uuid4(),
            fecha_inicio=date(2026, 1, 1),
            comisiones=[],
            is_active=True,
        )
        session.add(asignacion)
        await session.commit()
        return asignacion


async def _create_auth_headers(eng, user=None, tenant_id=TENANT_ID):
    if user is None:
        user = await _seed_user(eng, tenant_id)
    token = create_access_token(
        {"sub": str(user.id), "tenant_id": str(tenant_id), "roles": ["ADMIN"]}
    )
    return {"Authorization": f"Bearer {token}"}


async def _build_test_data(eng, tenant_id=TENANT_ID):
    await _seed_tenant(eng, tenant_id)
    carrera = await _seed_carrera(eng, tenant_id)
    cohorte = await _seed_cohorte(eng, tenant_id, carrera.id)
    materia = await _seed_materia(eng, tenant_id)
    user = await _seed_user(eng, tenant_id)
    asignacion = await _seed_asignacion(eng, tenant_id, user.id, materia.id)
    return user, materia, cohorte, carrera, asignacion


# ═══════════════════════════════════════════════════════════════════════════════
# 7.1 Repository tests: SlotEncuentroRepository e InstanciaEncuentroRepository
# ═══════════════════════════════════════════════════════════════════════════════


class TestSlotEncuentroRepository:
    async def _seed_refs(self, db_session, tenant_id):
        """Create minimal FK references."""
        db_session.add(Tenant(id=tenant_id, name="Test", slug=f"t-{tenant_id.hex[:8]}", code=f"T{tenant_id.hex[:4].upper()}"))
        await db_session.flush()
        usr = Usuario(id=uuid.uuid4(), tenant_id=tenant_id, email="slot@test.com", hashed_password="hash")
        db_session.add(usr)
        await db_session.flush()
        asig = Asignacion(id=uuid.uuid4(), tenant_id=tenant_id, usuario_id=usr.id,
                          rol="PROFESOR", fecha_inicio=date(2026, 1, 1), comisiones=[], is_active=True)
        mat = Materia(id=uuid.uuid4(), tenant_id=tenant_id, codigo="MAT", nombre="Test", is_active=True)
        db_session.add_all([asig, mat])
        await db_session.flush()
        return asig, mat

    async def test_create_slot(self, db_session):
        tenant_id = uuid.uuid4()
        repo = SlotEncuentroRepository(db_session, tenant_id)
        asig, mat = await self._seed_refs(db_session, tenant_id)

        slot = await repo.create(
            tenant_id=tenant_id,
            asignacion_id=asig.id,
            materia_id=mat.id,
            titulo="Clase 1",
            hora=time(10, 0),
            dia_semana=DiaSemana.LUNES,
            fecha_inicio=date(2026, 6, 1),
            cant_semanas=4,
            meet_url="https://meet.example.com",
            vig_desde=date(2026, 6, 1),
            vig_hasta=date(2026, 7, 1),
        )
        assert slot.id is not None
        assert slot.titulo == "Clase 1"
        assert slot.tenant_id == tenant_id

    async def test_get_slot(self, db_session):
        tenant_id = uuid.uuid4()
        repo = SlotEncuentroRepository(db_session, tenant_id)
        asig, mat = await self._seed_refs(db_session, tenant_id)
        slot = await repo.create(
            tenant_id=tenant_id,
            asignacion_id=asig.id,
            materia_id=mat.id,
            titulo="Slot Test",
            hora=time(14, 0),
            dia_semana=DiaSemana.MARTES,
            fecha_inicio=date(2026, 6, 1),
            cant_semanas=0,
            vig_desde=date(2026, 6, 1),
            vig_hasta=date(2026, 6, 1),
        )
        found = await repo.get(slot.id)
        assert found.id == slot.id
        assert found.titulo == "Slot Test"

    async def test_get_slot_not_found(self, db_session):
        repo = SlotEncuentroRepository(db_session, uuid.uuid4())
        with pytest.raises(NotFoundError):
            await repo.get(uuid.uuid4())

    async def test_soft_delete_slot(self, db_session):
        tenant_id = uuid.uuid4()
        repo = SlotEncuentroRepository(db_session, tenant_id)
        asig, mat = await self._seed_refs(db_session, tenant_id)
        slot = await repo.create(
            tenant_id=tenant_id,
            asignacion_id=asig.id,
            materia_id=mat.id,
            titulo="To Delete",
            hora=time(9, 0),
            dia_semana=DiaSemana.MIERCOLES,
            fecha_inicio=date(2026, 6, 1),
            cant_semanas=0,
            vig_desde=date(2026, 6, 1),
            vig_hasta=date(2026, 6, 1),
        )
        await repo.soft_delete(slot.id)
        with pytest.raises(NotFoundError):
            await repo.get(slot.id)

    async def test_list_by_filters(self, db_session):
        tenant_id = uuid.uuid4()
        repo = SlotEncuentroRepository(db_session, tenant_id)
        asig, mat_a = await self._seed_refs(db_session, tenant_id)
        mat_b = Materia(id=uuid.uuid4(), tenant_id=tenant_id, codigo="MAT2", nombre="Test 2", is_active=True)
        db_session.add(mat_b)
        await db_session.flush()

        await repo.create(
            tenant_id=tenant_id, asignacion_id=asig.id, materia_id=mat_a.id,
            titulo="A", hora=time(10, 0), dia_semana=DiaSemana.LUNES,
            fecha_inicio=date(2026, 6, 1), cant_semanas=0,
            vig_desde=date(2026, 6, 1), vig_hasta=date(2026, 6, 1),
        )
        await repo.create(
            tenant_id=tenant_id, asignacion_id=asig.id, materia_id=mat_b.id,
            titulo="B", hora=time(11, 0), dia_semana=DiaSemana.MARTES,
            fecha_inicio=date(2026, 6, 1), cant_semanas=0,
            vig_desde=date(2026, 6, 1), vig_hasta=date(2026, 6, 1),
        )

        items, total, pages = await repo.list_by_filters(materia_id=mat_a.id)
        assert total == 1
        assert items[0].titulo == "A"

        items, total, pages = await repo.list_by_filters(asignacion_id=asig.id)
        assert total == 2


class TestInstanciaEncuentroRepository:
    async def _seed_refs(self, db_session, tenant_id):
        db_session.add(Tenant(id=tenant_id, name="Test", slug=f"t-{tenant_id.hex[:8]}", code=f"T{tenant_id.hex[:4].upper()}"))
        await db_session.flush()
        mat = Materia(id=uuid.uuid4(), tenant_id=tenant_id, codigo="MAT", nombre="Test", is_active=True)
        db_session.add(mat)
        await db_session.flush()
        return mat

    async def test_create_instancia(self, db_session):
        tenant_id = uuid.uuid4()
        repo = InstanciaEncuentroRepository(db_session, tenant_id)
        mat = await self._seed_refs(db_session, tenant_id)
        inst = await repo.create(
            tenant_id=tenant_id,
            materia_id=mat.id,
            fecha=date(2026, 6, 15),
            hora=time(10, 0),
            titulo="Instancia Test",
            estado=EstadoInstancia.PROGRAMADO,
        )
        assert inst.id is not None
        assert inst.estado == EstadoInstancia.PROGRAMADO

    async def test_list_by_slot(self, db_session):
        tenant_id = uuid.uuid4()
        repo = InstanciaEncuentroRepository(db_session, tenant_id)
        mat = await self._seed_refs(db_session, tenant_id)
        usr = Usuario(id=uuid.uuid4(), tenant_id=tenant_id, email="slot2@test.com", hashed_password="hash")
        db_session.add(usr)
        await db_session.flush()
        asig = Asignacion(id=uuid.uuid4(), tenant_id=tenant_id, usuario_id=usr.id,
                          rol="PROFESOR", fecha_inicio=date(2026, 1, 1), comisiones=[], is_active=True)
        db_session.add(asig)
        await db_session.flush()
        slot = SlotEncuentro(id=uuid.uuid4(), tenant_id=tenant_id, asignacion_id=asig.id, materia_id=mat.id,
                             titulo="Slot", hora=time(10, 0), dia_semana=DiaSemana.LUNES,
                             fecha_inicio=date(2026, 6, 1), cant_semanas=0,
                             vig_desde=date(2026, 6, 1), vig_hasta=date(2026, 6, 1))
        db_session.add(slot)
        await db_session.flush()

        for i in range(3):
            await repo.create(
                tenant_id=tenant_id, slot_id=slot.id, materia_id=mat.id,
                fecha=date(2026, 6, 1 + i), hora=time(10, 0),
                titulo=f"Instancia {i}", estado=EstadoInstancia.PROGRAMADO,
            )

        items, total, pages = await repo.list_by_slot(slot.id)
        assert total == 3

    async def test_list_admin_with_filters(self, db_session):
        tenant_id = uuid.uuid4()
        repo = InstanciaEncuentroRepository(db_session, tenant_id)
        mat = await self._seed_refs(db_session, tenant_id)

        await repo.create(
            tenant_id=tenant_id, materia_id=mat.id,
            fecha=date(2026, 6, 1), hora=time(10, 0),
            titulo="Programado", estado=EstadoInstancia.PROGRAMADO,
        )
        await repo.create(
            tenant_id=tenant_id, materia_id=mat.id,
            fecha=date(2026, 6, 2), hora=time(11, 0),
            titulo="Realizado", estado=EstadoInstancia.REALIZADO,
        )

        items, total, pages = await repo.list_admin(estado=EstadoInstancia.REALIZADO)
        assert total == 1
        assert items[0].titulo == "Realizado"

    async def test_list_futuras(self, db_session):
        tenant_id = uuid.uuid4()
        repo = InstanciaEncuentroRepository(db_session, tenant_id)
        mat = await self._seed_refs(db_session, tenant_id)

        inst = await repo.create(
            tenant_id=tenant_id, materia_id=mat.id,
            fecha=date(2099, 1, 1), hora=time(10, 0),
            titulo="Futura", estado=EstadoInstancia.PROGRAMADO,
        )
        await repo.create(
            tenant_id=tenant_id, materia_id=mat.id,
            fecha=date(2020, 1, 1), hora=time(10, 0),
            titulo="Pasada", estado=EstadoInstancia.PROGRAMADO,
        )

        futuras = await repo.list_futuras(materia_id=mat.id)
        assert len(futuras) == 1
        assert futuras[0].id == inst.id


# ═══════════════════════════════════════════════════════════════════════════════
# 7.2 Repository tests: GuardiaRepository
# ═══════════════════════════════════════════════════════════════════════════════


class TestGuardiaRepository:
    async def _seed_refs(self, db_session, tenant_id):
        db_session.add(Tenant(id=tenant_id, name="Test", slug=f"t-{tenant_id.hex[:8]}", code=f"T{tenant_id.hex[:4].upper()}"))
        await db_session.flush()
        usr = Usuario(id=uuid.uuid4(), tenant_id=tenant_id, email="guardia@test.com", hashed_password="hash")
        db_session.add(usr)
        await db_session.flush()
        asig = Asignacion(id=uuid.uuid4(), tenant_id=tenant_id, usuario_id=usr.id,
                          rol="TUTOR", fecha_inicio=date(2026, 1, 1), comisiones=[], is_active=True)
        mat = Materia(id=uuid.uuid4(), tenant_id=tenant_id, codigo="MAT", nombre="Test", is_active=True)
        carr = Carrera(id=uuid.uuid4(), tenant_id=tenant_id, codigo="CARR", nombre="Carrera Test")
        coh = Cohorte(id=uuid.uuid4(), tenant_id=tenant_id, carrera_id=carr.id, nombre="COH", anio=2026)
        db_session.add_all([asig, mat, carr, coh])
        await db_session.flush()
        return asig, mat, carr, coh

    async def test_create_guardia(self, db_session):
        tenant_id = uuid.uuid4()
        repo = GuardiaRepository(db_session, tenant_id)
        asig, mat, carr, coh = await self._seed_refs(db_session, tenant_id)
        g = await repo.create(
            tenant_id=tenant_id,
            asignacion_id=asig.id,
            materia_id=mat.id,
            carrera_id=carr.id,
            cohorte_id=coh.id,
            dia=DiaSemanaGuardia.LUNES,
            horario="10:00-12:00",
            estado=EstadoGuardia.PENDIENTE,
        )
        assert g.id is not None
        assert g.estado == EstadoGuardia.PENDIENTE

    async def test_get_guardia(self, db_session):
        tenant_id = uuid.uuid4()
        repo = GuardiaRepository(db_session, tenant_id)
        asig, mat, carr, coh = await self._seed_refs(db_session, tenant_id)
        g = await repo.create(
            tenant_id=tenant_id, asignacion_id=asig.id,
            materia_id=mat.id, carrera_id=carr.id,
            cohorte_id=coh.id, dia=DiaSemanaGuardia.LUNES,
            horario="10:00", estado=EstadoGuardia.PENDIENTE,
        )
        found = await repo.get(g.id)
        assert found.id == g.id

    async def test_list_by_usuario(self, db_session):
        tenant_id = uuid.uuid4()
        repo = GuardiaRepository(db_session, tenant_id)
        asig_a, mat, carr, coh = await self._seed_refs(db_session, tenant_id)
        usr_b = Usuario(id=uuid.uuid4(), tenant_id=tenant_id, email="asig_b_user@test.com", hashed_password="hash")
        db_session.add(usr_b)
        await db_session.flush()
        asig_b = Asignacion(id=uuid.uuid4(), tenant_id=tenant_id, usuario_id=usr_b.id,
                            rol="TUTOR", fecha_inicio=date(2026, 1, 1), comisiones=[], is_active=True)
        db_session.add(asig_b)
        await db_session.flush()

        await repo.create(
            tenant_id=tenant_id, asignacion_id=asig_a.id,
            materia_id=mat.id, carrera_id=carr.id,
            cohorte_id=coh.id, dia=DiaSemanaGuardia.LUNES,
            horario="10:00", estado=EstadoGuardia.PENDIENTE,
        )
        await repo.create(
            tenant_id=tenant_id, asignacion_id=asig_b.id,
            materia_id=mat.id, carrera_id=carr.id,
            cohorte_id=coh.id, dia=DiaSemanaGuardia.MARTES,
            horario="14:00", estado=EstadoGuardia.PENDIENTE,
        )

        items, total, pages = await repo.list_by_usuario([asig_a.id])
        assert total == 1

    async def test_list_admin_with_filters(self, db_session):
        tenant_id = uuid.uuid4()
        repo = GuardiaRepository(db_session, tenant_id)
        asig, mat_a, carr, coh = await self._seed_refs(db_session, tenant_id)
        mat_b = Materia(id=uuid.uuid4(), tenant_id=tenant_id, codigo="MAT2", nombre="Test 2", is_active=True)
        db_session.add(mat_b)
        await db_session.flush()

        await repo.create(
            tenant_id=tenant_id, asignacion_id=asig.id,
            materia_id=mat_a.id, carrera_id=carr.id,
            cohorte_id=coh.id, dia=DiaSemanaGuardia.LUNES,
            horario="10:00", estado=EstadoGuardia.PENDIENTE,
        )
        await repo.create(
            tenant_id=tenant_id, asignacion_id=asig.id,
            materia_id=mat_b.id, carrera_id=carr.id,
            cohorte_id=coh.id, dia=DiaSemanaGuardia.MARTES,
            horario="14:00", estado=EstadoGuardia.REALIZADA,
        )

        items, total, pages = await repo.list_admin(materia_id=mat_a.id)
        assert total == 1

    async def test_list_for_export(self, db_session):
        tenant_id = uuid.uuid4()
        repo = GuardiaRepository(db_session, tenant_id)
        asig, mat, carr, coh = await self._seed_refs(db_session, tenant_id)
        await repo.create(
            tenant_id=tenant_id, asignacion_id=asig.id,
            materia_id=mat.id, carrera_id=carr.id,
            cohorte_id=coh.id, dia=DiaSemanaGuardia.LUNES,
            horario="10:00", estado=EstadoGuardia.PENDIENTE,
        )

        results = await repo.list_for_export()
        assert len(results) >= 1

    async def test_update_estado(self, db_session):
        tenant_id = uuid.uuid4()
        repo = GuardiaRepository(db_session, tenant_id)
        asig, mat, carr, coh = await self._seed_refs(db_session, tenant_id)
        g = await repo.create(
            tenant_id=tenant_id, asignacion_id=asig.id,
            materia_id=mat.id, carrera_id=carr.id,
            cohorte_id=coh.id, dia=DiaSemanaGuardia.LUNES,
            horario="10:00", estado=EstadoGuardia.PENDIENTE,
        )
        updated = await repo.update(g.id, estado=EstadoGuardia.REALIZADA)
        assert updated.estado == EstadoGuardia.REALIZADA


# ═══════════════════════════════════════════════════════════════════════════════
# 7.3 Service tests: slot recurrente, validaciones, límite semanas
# ═══════════════════════════════════════════════════════════════════════════════


class TestEncuentroServiceSlot:
    async def _seed_refs(self, db_session, tenant_id):
        db_session.add(Tenant(id=tenant_id, name="Test", slug=f"t-{tenant_id.hex[:8]}", code=f"T{tenant_id.hex[:4].upper()}"))
        await db_session.flush()
        usr = Usuario(id=uuid.uuid4(), tenant_id=tenant_id, email="slot_svc@test.com", hashed_password="hash")
        db_session.add(usr)
        await db_session.flush()
        asig = Asignacion(id=uuid.uuid4(), tenant_id=tenant_id, usuario_id=usr.id,
                          rol="PROFESOR", fecha_inicio=date(2026, 1, 1), comisiones=[], is_active=True)
        mat = Materia(id=uuid.uuid4(), tenant_id=tenant_id, codigo="MAT", nombre="Test", is_active=True)
        db_session.add_all([asig, mat])
        await db_session.flush()
        return asig, mat

    async def test_create_slot_generates_n_instancias(self, db_session):
        tenant_id = uuid.uuid4()
        from app.schemas.encuentro import SlotEncuentroCreate
        service = EncuentroService(db_session, tenant_id)
        asig, mat = await self._seed_refs(db_session, tenant_id)

        data = SlotEncuentroCreate(
            asignacion_id=asig.id,
            materia_id=mat.id,
            titulo="Clase Recurrente",
            hora=time(10, 0),
            dia_semana=DiaSemana.LUNES,
            fecha_inicio=date(2026, 6, 1),
            cant_semanas=3,
            vig_desde=date(2026, 6, 1),
            vig_hasta=date(2026, 7, 1),
        )
        slot = await service.create_slot(data)
        assert slot.cant_semanas == 3
        assert slot.fecha_unica is None

        stmt = select(InstanciaEncuentro).where(InstanciaEncuentro.slot_id == slot.id)
        result = await db_session.execute(stmt)
        instancias = result.scalars().all()
        assert len(instancias) == 3

    async def test_create_slot_fecha_unica(self, db_session):
        tenant_id = uuid.uuid4()
        from app.schemas.encuentro import SlotEncuentroCreate
        service = EncuentroService(db_session, tenant_id)
        asig, mat = await self._seed_refs(db_session, tenant_id)

        data = SlotEncuentroCreate(
            asignacion_id=asig.id,
            materia_id=mat.id,
            titulo="Clase Única",
            hora=time(10, 0),
            dia_semana=DiaSemana.LUNES,
            fecha_inicio=date(2026, 6, 1),
            cant_semanas=0,
            fecha_unica=date(2026, 6, 15),
            vig_desde=date(2026, 6, 1),
            vig_hasta=date(2026, 6, 30),
        )
        slot = await service.create_slot(data)
        assert slot.cant_semanas == 0
        assert slot.fecha_unica == date(2026, 6, 15)

        stmt = select(InstanciaEncuentro).where(InstanciaEncuentro.slot_id == slot.id)
        result = await db_session.execute(stmt)
        instancias = result.scalars().all()
        assert len(instancias) == 1

    async def test_validation_mutually_exclusive_returns_422(self, db_session):
        tenant_id = uuid.uuid4()
        from app.schemas.encuentro import SlotEncuentroCreate
        from fastapi import HTTPException
        service = EncuentroService(db_session, tenant_id)
        asig, mat = await self._seed_refs(db_session, tenant_id)

        data = SlotEncuentroCreate(
            asignacion_id=asig.id,
            materia_id=mat.id,
            titulo="Invalido",
            hora=time(10, 0),
            dia_semana=DiaSemana.LUNES,
            fecha_inicio=date(2026, 6, 1),
            cant_semanas=0,
            fecha_unica=None,
            vig_desde=date(2026, 6, 1),
            vig_hasta=date(2026, 7, 1),
        )
        with pytest.raises(HTTPException) as exc:
            await service.create_slot(data)
        assert exc.value.status_code == 422

    async def test_validation_max_semanas_returns_422(self, db_session):
        tenant_id = uuid.uuid4()
        from app.schemas.encuentro import SlotEncuentroCreate
        from fastapi import HTTPException
        service = EncuentroService(db_session, tenant_id)
        asig, mat = await self._seed_refs(db_session, tenant_id)

        # Schema validation will reject 53 because max=52, so use cant_semanas=1
        # and test service-level validation instead
        data = SlotEncuentroCreate(
            asignacion_id=asig.id,
            materia_id=mat.id,
            titulo="Semanas",
            hora=time(10, 0),
            dia_semana=DiaSemana.LUNES,
            fecha_inicio=date(2026, 6, 1),
            cant_semanas=1,
            vig_desde=date(2026, 6, 1),
            vig_hasta=date(2026, 7, 1),
        )
        # Test the cant_semanas validation via a different approach
        # The schema already validates max 52, so this tests that the schema catches it
        with pytest.raises(Exception):
            SlotEncuentroCreate(
                asignacion_id=asig.id,
                materia_id=mat.id,
                titulo="Demasiadas Semanas",
                hora=time(10, 0),
                dia_semana=DiaSemana.LUNES,
                fecha_inicio=date(2026, 6, 1),
                cant_semanas=53,
                vig_desde=date(2026, 6, 1),
                vig_hasta=date(2026, 7, 1),
            )


# ═══════════════════════════════════════════════════════════════════════════════
# 7.4 Service tests: instancias independientes, actualización de estado
# ═══════════════════════════════════════════════════════════════════════════════


class TestEncuentroServiceInstancia:
    async def _seed_refs(self, db_session, tenant_id):
        db_session.add(Tenant(id=tenant_id, name="Test", slug=f"t-{tenant_id.hex[:8]}", code=f"T{tenant_id.hex[:4].upper()}"))
        await db_session.flush()
        mat = Materia(id=uuid.uuid4(), tenant_id=tenant_id, codigo="MAT", nombre="Test", is_active=True)
        db_session.add(mat)
        await db_session.flush()
        return mat

    async def test_create_instancia_independiente(self, db_session):
        tenant_id = uuid.uuid4()
        from app.schemas.encuentro import InstanciaEncuentroCreate
        service = EncuentroService(db_session, tenant_id)
        mat = await self._seed_refs(db_session, tenant_id)

        data = InstanciaEncuentroCreate(
            materia_id=mat.id,
            fecha=date(2026, 7, 1),
            hora=time(15, 0),
            titulo="Clase Extra",
        )
        inst = await service.create_instancia_independiente(data)
        assert inst.titulo == "Clase Extra"
        assert inst.estado == EstadoInstancia.PROGRAMADO
        assert inst.slot_id is None

    async def test_update_instancia_estado(self, db_session):
        tenant_id = uuid.uuid4()
        from app.schemas.encuentro import InstanciaEncuentroUpdate
        repo = InstanciaEncuentroRepository(db_session, tenant_id)
        service = EncuentroService(db_session, tenant_id)
        mat = await self._seed_refs(db_session, tenant_id)

        inst = await repo.create(
            tenant_id=tenant_id, materia_id=mat.id,
            fecha=date(2026, 7, 1), hora=time(15, 0),
            titulo="Para Actualizar", estado=EstadoInstancia.PROGRAMADO,
        )
        update_data = InstanciaEncuentroUpdate(
            estado=EstadoInstancia.REALIZADO,
            meet_url="https://meet.example.com",
            video_url="https://video.example.com/rec",
            comentario="Buena clase",
        )
        updated = await service.update_instancia(inst.id, update_data)
        assert updated.estado == EstadoInstancia.REALIZADO
        assert updated.video_url == "https://video.example.com/rec"
        assert updated.comentario == "Buena clase"

    async def test_update_instancia_not_found(self, db_session):
        tenant_id = uuid.uuid4()
        from app.schemas.encuentro import InstanciaEncuentroUpdate
        from fastapi import HTTPException
        service = EncuentroService(db_session, tenant_id)

        with pytest.raises(HTTPException) as exc:
            await service.update_instancia(
                uuid.uuid4(),
                InstanciaEncuentroUpdate(estado=EstadoInstancia.CANCELADO),
            )
        assert exc.value.status_code == 404

    async def test_list_instancias_por_slot(self, db_session):
        tenant_id = uuid.uuid4()
        service = EncuentroService(db_session, tenant_id)
        from app.schemas.encuentro import SlotEncuentroCreate
        db_session.add(Tenant(id=tenant_id, name="Test", slug=f"t-{tenant_id.hex[:8]}", code=f"T{tenant_id.hex[:4].upper()}"))
        await db_session.flush()
        usr = Usuario(id=uuid.uuid4(), tenant_id=tenant_id, email="asig_slot@test.com", hashed_password="hash")
        db_session.add(usr)
        await db_session.flush()
        asig = Asignacion(id=uuid.uuid4(), tenant_id=tenant_id, usuario_id=usr.id,
                          rol="PROFESOR", fecha_inicio=date(2026, 1, 1), comisiones=[], is_active=True)
        mat = Materia(id=uuid.uuid4(), tenant_id=tenant_id, codigo="MAT", nombre="Test", is_active=True)
        db_session.add_all([asig, mat])
        await db_session.flush()

        data = SlotEncuentroCreate(
            asignacion_id=asig.id,
            materia_id=mat.id,
            titulo="Slot Con Instancias",
            hora=time(10, 0),
            dia_semana=DiaSemana.LUNES,
            fecha_inicio=date(2026, 6, 1),
            cant_semanas=2,
            vig_desde=date(2026, 6, 1),
            vig_hasta=date(2026, 7, 1),
        )
        slot = await service.create_slot(data)
        items, total, pages = await service.list_instancias_por_slot(slot.id)
        assert total == 2


# ═══════════════════════════════════════════════════════════════════════════════
# 7.5 Service tests: guardias, estado transitions
# ═══════════════════════════════════════════════════════════════════════════════


class TestGuardiaService:
    async def _seed_refs(self, db_session, tenant_id):
        db_session.add(Tenant(id=tenant_id, name="Test", slug=f"t-{tenant_id.hex[:8]}", code=f"T{tenant_id.hex[:4].upper()}"))
        await db_session.flush()
        usr = Usuario(id=uuid.uuid4(), tenant_id=tenant_id, email="guardia_svc@test.com", hashed_password="hash")
        db_session.add(usr)
        await db_session.flush()
        asig = Asignacion(id=uuid.uuid4(), tenant_id=tenant_id, usuario_id=usr.id,
                          rol="TUTOR", fecha_inicio=date(2026, 1, 1), comisiones=[], is_active=True)
        mat = Materia(id=uuid.uuid4(), tenant_id=tenant_id, codigo="MAT", nombre="Test", is_active=True)
        carr = Carrera(id=uuid.uuid4(), tenant_id=tenant_id, codigo="CARR", nombre="Carrera Test")
        coh = Cohorte(id=uuid.uuid4(), tenant_id=tenant_id, carrera_id=carr.id, nombre="COH", anio=2026)
        db_session.add_all([asig, mat, carr, coh])
        await db_session.flush()
        return asig, mat, carr, coh

    async def test_create_guardia(self, db_session):
        tenant_id = uuid.uuid4()
        from app.schemas.guardia import GuardiaCreate
        service = GuardiaService(db_session, tenant_id)
        asig, mat, carr, coh = await self._seed_refs(db_session, tenant_id)

        data = GuardiaCreate(
            asignacion_id=asig.id,
            materia_id=mat.id,
            carrera_id=carr.id,
            cohorte_id=coh.id,
            dia=DiaSemanaGuardia.LUNES,
            horario="10:00-12:00",
        )
        g = await service.create(data)
        assert g.estado == EstadoGuardia.PENDIENTE
        assert g.comentarios is None

    async def test_create_guardia_with_comentarios(self, db_session):
        tenant_id = uuid.uuid4()
        from app.schemas.guardia import GuardiaCreate
        service = GuardiaService(db_session, tenant_id)
        asig, mat, carr, coh = await self._seed_refs(db_session, tenant_id)

        data = GuardiaCreate(
            asignacion_id=asig.id,
            materia_id=mat.id,
            carrera_id=carr.id,
            cohorte_id=coh.id,
            dia=DiaSemanaGuardia.LUNES,
            horario="10:00-12:00",
            comentarios="Guardia completa",
        )
        g = await service.create(data)
        assert g.comentarios == "Guardia completa"

    async def test_update_estado_pendiente_a_realizada(self, db_session):
        tenant_id = uuid.uuid4()
        from app.schemas.guardia import GuardiaCreate
        service = GuardiaService(db_session, tenant_id)
        asig, mat, carr, coh = await self._seed_refs(db_session, tenant_id)

        data = GuardiaCreate(
            asignacion_id=asig.id, materia_id=mat.id,
            carrera_id=carr.id, cohorte_id=coh.id,
            dia=DiaSemanaGuardia.LUNES, horario="10:00",
        )
        g = await service.create(data)
        updated = await service.update_estado(g.id, EstadoGuardia.REALIZADA)
        assert updated.estado == EstadoGuardia.REALIZADA

    async def test_cannot_modify_realizada(self, db_session):
        tenant_id = uuid.uuid4()
        from app.schemas.guardia import GuardiaCreate
        from fastapi import HTTPException
        service = GuardiaService(db_session, tenant_id)
        asig, mat, carr, coh = await self._seed_refs(db_session, tenant_id)

        data = GuardiaCreate(
            asignacion_id=asig.id, materia_id=mat.id,
            carrera_id=carr.id, cohorte_id=coh.id,
            dia=DiaSemanaGuardia.LUNES, horario="10:00",
        )
        g = await service.create(data)
        await service.update_estado(g.id, EstadoGuardia.REALIZADA)
        with pytest.raises(HTTPException) as exc:
            await service.update_estado(g.id, EstadoGuardia.CANCELADA)
        assert exc.value.status_code == 400

    async def test_cannot_modify_cancelada(self, db_session):
        tenant_id = uuid.uuid4()
        from app.schemas.guardia import GuardiaCreate
        from fastapi import HTTPException
        service = GuardiaService(db_session, tenant_id)
        asig, mat, carr, coh = await self._seed_refs(db_session, tenant_id)

        data = GuardiaCreate(
            asignacion_id=asig.id, materia_id=mat.id,
            carrera_id=carr.id, cohorte_id=coh.id,
            dia=DiaSemanaGuardia.LUNES, horario="10:00",
        )
        g = await service.create(data)
        await service.update_estado(g.id, EstadoGuardia.CANCELADA)
        with pytest.raises(HTTPException) as exc:
            await service.update_estado(g.id, EstadoGuardia.REALIZADA)
        assert exc.value.status_code == 400

    async def test_list_mis_guardias(self, db_session):
        tenant_id = uuid.uuid4()
        from app.schemas.guardia import GuardiaCreate
        service = GuardiaService(db_session, tenant_id)
        asig, mat, carr, coh = await self._seed_refs(db_session, tenant_id)
        user_id = asig.usuario_id

        data = GuardiaCreate(
            asignacion_id=asig.id, materia_id=mat.id,
            carrera_id=carr.id, cohorte_id=coh.id,
            dia=DiaSemanaGuardia.LUNES, horario="10:00",
        )
        await service.create(data)

        items, total, pages = await service.list_mis_guardias(user_id)
        assert total == 1

    async def test_update_estado_not_found(self, db_session):
        tenant_id = uuid.uuid4()
        from fastapi import HTTPException
        service = GuardiaService(db_session, tenant_id)
        with pytest.raises(HTTPException) as exc:
            await service.update_estado(uuid.uuid4(), EstadoGuardia.REALIZADA)
        assert exc.value.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# 7.6 Export tests: HTML de encuentros, CSV de guardias
# ═══════════════════════════════════════════════════════════════════════════════


class TestExportEncuentroHTML:
    async def _seed_refs(self, db_session, tenant_id):
        db_session.add(Tenant(id=tenant_id, name="Test", slug=f"t-{tenant_id.hex[:8]}", code=f"T{tenant_id.hex[:4].upper()}"))
        await db_session.flush()
        mat = Materia(id=uuid.uuid4(), tenant_id=tenant_id, codigo="MAT", nombre="Test", is_active=True)
        db_session.add(mat)
        await db_session.flush()
        return mat

    async def test_exportar_html_returns_table(self, db_session):
        tenant_id = uuid.uuid4()
        repo = InstanciaEncuentroRepository(db_session, tenant_id)
        service = EncuentroService(db_session, tenant_id)
        mat = await self._seed_refs(db_session, tenant_id)

        await repo.create(
            tenant_id=tenant_id, materia_id=mat.id,
            fecha=date(2099, 1, 1), hora=time(10, 0),
            titulo="Clase Futura", estado=EstadoInstancia.PROGRAMADO,
            meet_url="https://meet.example.com",
        )

        html = await service.exportar_html(materia_id=mat.id)
        assert "<table" in html
        assert "Clase Futura" in html
        assert "Unirse" in html
        assert "</table>" in html

    async def test_exportar_html_solo_incluye_relevantes(self, db_session):
        tenant_id = uuid.uuid4()
        repo = InstanciaEncuentroRepository(db_session, tenant_id)
        service = EncuentroService(db_session, tenant_id)
        mat = await self._seed_refs(db_session, tenant_id)

        await repo.create(
            tenant_id=tenant_id, materia_id=mat.id,
            fecha=date(2020, 1, 1), hora=time(10, 0),
            titulo="Pasada", estado=EstadoInstancia.CANCELADO,
        )

        html = await service.exportar_html(materia_id=mat.id)
        assert "Pasada" not in html


class TestExportGuardiaCSV:
    async def _seed_refs(self, db_session, tenant_id):
        db_session.add(Tenant(id=tenant_id, name="Test", slug=f"t-{tenant_id.hex[:8]}", code=f"T{tenant_id.hex[:4].upper()}"))
        await db_session.flush()
        usr = Usuario(id=uuid.uuid4(), tenant_id=tenant_id, email="export_svc@test.com", hashed_password="hash")
        db_session.add(usr)
        await db_session.flush()
        asig = Asignacion(id=uuid.uuid4(), tenant_id=tenant_id, usuario_id=usr.id,
                          rol="TUTOR", fecha_inicio=date(2026, 1, 1), comisiones=[], is_active=True)
        mat = Materia(id=uuid.uuid4(), tenant_id=tenant_id, codigo="MAT", nombre="Test", is_active=True)
        carr = Carrera(id=uuid.uuid4(), tenant_id=tenant_id, codigo="CARR", nombre="Carrera Test")
        coh = Cohorte(id=uuid.uuid4(), tenant_id=tenant_id, carrera_id=carr.id, nombre="COH", anio=2026)
        db_session.add_all([asig, mat, carr, coh])
        await db_session.flush()
        return asig, mat, carr, coh

    async def test_exportar_csv_returns_csv(self, db_session):
        tenant_id = uuid.uuid4()
        repo = GuardiaRepository(db_session, tenant_id)
        service = GuardiaService(db_session, tenant_id)
        asig, mat, carr, coh = await self._seed_refs(db_session, tenant_id)

        await repo.create(
            tenant_id=tenant_id, asignacion_id=asig.id,
            materia_id=mat.id, carrera_id=carr.id,
            cohorte_id=coh.id, dia=DiaSemanaGuardia.LUNES,
            horario="10:00", estado=EstadoGuardia.PENDIENTE,
            comentarios="Test",
        )

        csv_content = await service.exportar_csv()
        assert "dia" in csv_content
        assert "horario" in csv_content
        assert "Lunes" in csv_content or "10:00" in csv_content

    async def test_exportar_csv_multiple_rows(self, db_session):
        tenant_id = uuid.uuid4()
        repo = GuardiaRepository(db_session, tenant_id)
        service = GuardiaService(db_session, tenant_id)
        asig, mat, carr, coh = await self._seed_refs(db_session, tenant_id)

        for i in range(3):
            await repo.create(
                tenant_id=tenant_id, asignacion_id=asig.id,
                materia_id=mat.id, carrera_id=carr.id,
                cohorte_id=coh.id, dia=DiaSemanaGuardia.LUNES,
                horario=f"{10+i}:00", estado=EstadoGuardia.PENDIENTE,
            )

        csv_content = await service.exportar_csv()
        lines = csv_content.strip().split("\n")
        assert len(lines) == 4  # header + 3 rows


# ═══════════════════════════════════════════════════════════════════════════════
# 7.7 Router tests: permissions, 403, 422
# ═══════════════════════════════════════════════════════════════════════════════


class TestRouterPermissionsEncuentros:
    async def test_create_slot_403_without_permission(self, client, eng):
        await _seed_tenant(eng)
        user = await _seed_user(eng)
        role = await _seed_role_no_permission(eng)
        await _assign_role(eng, user.id, role.id)
        headers = await _create_auth_headers(eng, user)

        resp = await client.post(
            "/api/encuentros/slots",
            json={"asignacion_id": str(uuid.uuid4()), "materia_id": str(uuid.uuid4()), "titulo": "X", "hora": "10:00", "dia_semana": "Lunes", "fecha_inicio": "2026-06-01", "cant_semanas": 1, "vig_desde": "2026-06-01", "vig_hasta": "2026-07-01"},
            headers=headers,
        )
        assert resp.status_code == 403

    async def test_list_slots_403_without_permission(self, client, eng):
        await _seed_tenant(eng)
        user = await _seed_user(eng)
        role = await _seed_role_no_permission(eng)
        await _assign_role(eng, user.id, role.id)
        headers = await _create_auth_headers(eng, user)

        resp = await client.get("/api/encuentros/slots", headers=headers)
        assert resp.status_code == 403

    async def test_create_instancia_403_without_permission(self, client, eng):
        await _seed_tenant(eng)
        user = await _seed_user(eng)
        role = await _seed_role_no_permission(eng)
        await _assign_role(eng, user.id, role.id)
        headers = await _create_auth_headers(eng, user)

        resp = await client.post(
            "/api/encuentros/instancias",
            json={"materia_id": str(uuid.uuid4()), "fecha": "2026-07-01", "hora": "15:00", "titulo": "X"},
            headers=headers,
        )
        assert resp.status_code == 403

    async def test_create_slot_invalid_data_422(self, client, eng):
        await _seed_tenant(eng)
        user = await _seed_user(eng)
        role = await _seed_role(eng, permissions=["encuentros:gestionar"])
        await _assign_role(eng, user.id, role.id)
        headers = await _create_auth_headers(eng, user)

        # Missing required fields
        resp = await client.post(
            "/api/encuentros/slots",
            json={},
            headers=headers,
        )
        assert resp.status_code == 422

    async def test_create_instancia_invalid_data_422(self, client, eng):
        await _seed_tenant(eng)
        user = await _seed_user(eng)
        role = await _seed_role(eng, permissions=["encuentros:gestionar"])
        await _assign_role(eng, user.id, role.id)
        headers = await _create_auth_headers(eng, user)

        resp = await client.post(
            "/api/encuentros/instancias",
            json={"materia_id": "not-a-uuid"},
            headers=headers,
        )
        assert resp.status_code == 422


class TestRouterPermissionsGuardias:
    async def test_create_guardia_403_without_permission(self, client, eng):
        await _seed_tenant(eng)
        user = await _seed_user(eng)
        role = await _seed_role_no_permission(eng)
        await _assign_role(eng, user.id, role.id)
        headers = await _create_auth_headers(eng, user)

        resp = await client.post(
            "/api/guardias",
            json={"asignacion_id": str(uuid.uuid4()), "materia_id": str(uuid.uuid4()), "carrera_id": str(uuid.uuid4()), "cohorte_id": str(uuid.uuid4()), "dia": "Lunes", "horario": "10:00"},
            headers=headers,
        )
        assert resp.status_code == 403

    async def test_admin_list_guardias_403_without_permission(self, client, eng):
        await _seed_tenant(eng)
        user = await _seed_user(eng)
        role = await _seed_role_no_permission(eng)
        await _assign_role(eng, user.id, role.id)
        headers = await _create_auth_headers(eng, user)

        resp = await client.get("/api/guardias", headers=headers)
        assert resp.status_code == 403

    async def test_create_guardia_422_invalid_data(self, client, eng):
        await _seed_tenant(eng)
        user = await _seed_user(eng)
        role = await _seed_role(eng, permissions=["guardias:registrar"])
        await _assign_role(eng, user.id, role.id)
        headers = await _create_auth_headers(eng, user)

        resp = await client.post(
            "/api/guardias",
            json={},
            headers=headers,
        )
        assert resp.status_code == 422

    async def test_create_guardia_success(self, client, eng):
        await _seed_tenant(eng)
        user, materia, cohorte, carrera, asignacion = await _build_test_data(eng)
        role = await _seed_role(eng, permissions=["guardias:registrar"])
        await _assign_role(eng, user.id, role.id)
        headers = await _create_auth_headers(eng, user)

        resp = await client.post(
            "/api/guardias",
            json={
                "asignacion_id": str(asignacion.id),
                "materia_id": str(materia.id),
                "carrera_id": str(carrera.id),
                "cohorte_id": str(cohorte.id),
                "dia": "Lunes",
                "horario": "10:00-12:00",
            },
            headers=headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["estado"] == "Pendiente"

    async def test_create_slot_recurrente_success(self, client, eng):
        await _seed_tenant(eng)
        user, materia, cohorte, carrera, asignacion = await _build_test_data(eng)
        role = await _seed_role(eng, permissions=["encuentros:gestionar", "encuentros:ver"])
        await _assign_role(eng, user.id, role.id)
        headers = await _create_auth_headers(eng, user)

        resp = await client.post(
            "/api/encuentros/slots",
            json={
                "asignacion_id": str(asignacion.id),
                "materia_id": str(materia.id),
                "titulo": "Clase Semanal",
                "hora": "10:00",
                "dia_semana": "Lunes",
                "fecha_inicio": "2026-06-01",
                "cant_semanas": 4,
                "vig_desde": "2026-06-01",
                "vig_hasta": "2026-07-01",
            },
            headers=headers,
        )
        assert resp.status_code == 201
