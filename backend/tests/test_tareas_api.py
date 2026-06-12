"""Integration tests for tareas endpoints."""
import os
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base, close_db_engine
from app.core.security import create_access_token, hash_password
from app.models.role import Role
from app.models.tarea import EstadoTarea, Tarea
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.models.usuario_role import UsuarioRole
from app.models.carrera import Carrera
from app.models.materia import Materia
from app.models.comentario_tarea import ComentarioTarea

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


async def _seed_materia(eng, tenant_id=TENANT_ID):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        carrera = Carrera(id=uuid.uuid4(), tenant_id=tenant_id, nombre="Carrera Test", codigo="CT")
        session.add(carrera)
        await session.flush()
        materia = Materia(id=uuid.uuid4(), tenant_id=tenant_id, nombre="Materia Test", codigo="MT",
                          carrera_id=carrera.id)
        session.add(materia)
        await session.commit()
        return materia


async def _seed_tarea(eng, tenant_id=TENANT_ID, asignado_a=None, asignado_por=None,
                      estado=EstadoTarea.PENDIENTE, descripcion="Tarea de prueba"):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        tarea = Tarea(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            estado=estado,
            asignado_a=asignado_a,
            asignado_por=asignado_por,
            descripcion=descripcion,
        )
        session.add(tarea)
        await session.commit()
        return tarea


async def _seed_comentario(eng, tarea_id, autor_id, texto="Comentario test"):
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        c = ComentarioTarea(
            id=uuid.uuid4(),
            tenant_id=TENANT_ID,
            tarea_id=tarea_id,
            autor_id=autor_id,
            texto=texto,
        )
        session.add(c)
        await session.commit()
        return c


class TestTareasCrud:
    async def test_create_tarea(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            profesor = await _seed_user(eng, email="profesor@test.com")
            role = await _seed_role(eng, permissions=["tareas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["PROFESOR"]},
            )
            async with await _make_app() as client:
                response = await client.post(
                    "/api/tareas/",
                    json={
                        "asignado_a": str(user.id),
                        "descripcion": "Tarea importante",
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 201
            data = response.json()
            assert data["descripcion"] == "Tarea importante"
            assert data["estado"] == "Pendiente"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_create_tarea_with_materia(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            materia = await _seed_materia(eng)
            role = await _seed_role(eng, permissions=["tareas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["PROFESOR"]},
            )
            async with await _make_app() as client:
                response = await client.post(
                    "/api/tareas/",
                    json={
                        "asignado_a": str(user.id),
                        "descripcion": "Tarea con materia",
                        "materia_id": str(materia.id),
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 201
            data = response.json()
            assert data["materia_id"] is not None
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_get_tarea(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["tareas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["PROFESOR"]},
            )
            tarea = await _seed_tarea(eng, asignado_a=user.id, asignado_por=user.id)
            async with await _make_app() as client:
                response = await client.get(
                    f"/api/tareas/{tarea.id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["id"] == str(tarea.id)
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_get_tarea_404(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["tareas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["PROFESOR"]},
            )
            async with await _make_app() as client:
                response = await client.get(
                    f"/api/tareas/{uuid.uuid4()}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 404
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_update_tarea_descripcion(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["tareas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["PROFESOR"]},
            )
            tarea = await _seed_tarea(eng, asignado_a=user.id, asignado_por=user.id)
            async with await _make_app() as client:
                response = await client.patch(
                    f"/api/tareas/{tarea.id}",
                    json={"descripcion": "Actualizada"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["descripcion"] == "Actualizada"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_reasignar_tarea(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user1 = await _seed_user(eng, email="user1@test.com")
            user2 = await _seed_user(eng, email="user2@test.com")
            role = await _seed_role(eng, permissions=["tareas:gestionar"])
            await _assign_role(eng, user1.id, role.id)
            token = create_access_token(
                {"sub": str(user1.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            tarea = await _seed_tarea(eng, asignado_a=user1.id, asignado_por=user1.id)
            async with await _make_app() as client:
                response = await client.patch(
                    f"/api/tareas/{tarea.id}",
                    json={"asignado_a": str(user2.id)},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["asignado_a"] == str(user2.id)
        finally:
            await _teardown_db()
            await eng.dispose()


class TestMisTareas:
    async def test_mis_tareas_returns_only_assigned(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user1 = await _seed_user(eng, email="user1@test.com")
            user2 = await _seed_user(eng, email="user2@test.com")
            role = await _seed_role(eng, permissions=["tareas:gestionar"])
            await _assign_role(eng, user1.id, role.id)
            await _assign_role(eng, user2.id, role.id)
            token1 = create_access_token(
                {"sub": str(user1.id), "tenant_id": str(TENANT_ID), "roles": ["PROFESOR"]},
            )
            await _seed_tarea(eng, asignado_a=user1.id, asignado_por=user1.id, descripcion="Tarea de user1")
            await _seed_tarea(eng, asignado_a=user2.id, asignado_por=user1.id, descripcion="Tarea de user2")
            async with await _make_app() as client:
                response = await client.get(
                    "/api/tareas/",
                    headers={"Authorization": f"Bearer {token1}"},
                )
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert data["items"][0]["descripcion"] == "Tarea de user1"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_mis_tareas_empty(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["tareas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["PROFESOR"]},
            )
            async with await _make_app() as client:
                response = await client.get(
                    "/api/tareas/",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["total"] == 0
        finally:
            await _teardown_db()
            await eng.dispose()


class TestTareasAdmin:
    async def test_admin_list_returns_all(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["tareas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            await _seed_tarea(eng, asignado_a=user.id, asignado_por=user.id, descripcion="Tarea 1")
            await _seed_tarea(eng, asignado_a=user.id, asignado_por=user.id, descripcion="Tarea 2")
            async with await _make_app() as client:
                response = await client.get(
                    "/api/tareas/admin",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["total"] == 2
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_admin_list_filtered_by_estado(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["tareas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            await _seed_tarea(eng, asignado_a=user.id, asignado_por=user.id, descripcion="Pendiente")
            await _seed_tarea(eng, asignado_a=user.id, asignado_por=user.id,
                              estado=EstadoTarea.RESUELTA, descripcion="Resuelta")
            async with await _make_app() as client:
                response = await client.get(
                    "/api/tareas/admin?estado=Pendiente",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["total"] == 1
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_admin_list_filtered_by_q(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["tareas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            await _seed_tarea(eng, asignado_a=user.id, asignado_por=user.id, descripcion="correccion de examen")
            await _seed_tarea(eng, asignado_a=user.id, asignado_por=user.id, descripcion="otra cosa")
            async with await _make_app() as client:
                response = await client.get(
                    "/api/tareas/admin?q=correccion",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["total"] == 1
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_admin_list_non_coord_returns_403(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng, name="PROFESOR", permissions=["tareas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["PROFESOR"]},
            )
            async with await _make_app() as client:
                response = await client.get(
                    "/api/tareas/admin",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()


class TestStateMachine:
    async def test_pendiente_to_en_progreso(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["tareas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["PROFESOR"]},
            )
            tarea = await _seed_tarea(eng, asignado_a=user.id, asignado_por=user.id)
            async with await _make_app() as client:
                response = await client.patch(
                    f"/api/tareas/{tarea.id}",
                    json={"estado": "En progreso"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["estado"] == "En progreso"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_en_progreso_to_resuelta(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["tareas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["PROFESOR"]},
            )
            tarea = await _seed_tarea(eng, asignado_a=user.id, asignado_por=user.id,
                                      estado=EstadoTarea.EN_PROGRESO)
            async with await _make_app() as client:
                response = await client.patch(
                    f"/api/tareas/{tarea.id}",
                    json={"estado": "Resuelta"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["estado"] == "Resuelta"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_invalid_transition_409(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["tareas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["PROFESOR"]},
            )
            tarea = await _seed_tarea(eng, asignado_a=user.id, asignado_por=user.id,
                                      estado=EstadoTarea.RESUELTA)
            async with await _make_app() as client:
                response = await client.patch(
                    f"/api/tareas/{tarea.id}",
                    json={"estado": "Pendiente"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 409
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_coordinador_cancela_desde_cualquier_estado(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            coord = await _seed_user(eng, email="coord@test.com")
            user = await _seed_user(eng, email="user@test.com")
            role = await _seed_role(eng, permissions=["tareas:gestionar"])
            await _assign_role(eng, coord.id, role.id)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(coord.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            tarea = await _seed_tarea(eng, asignado_a=user.id, asignado_por=coord.id,
                                      estado=EstadoTarea.EN_PROGRESO)
            async with await _make_app() as client:
                response = await client.patch(
                    f"/api/tareas/{tarea.id}",
                    json={"estado": "Cancelada"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["estado"] == "Cancelada"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_coordinador_devuelve_resuelta_a_pendiente(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            coord = await _seed_user(eng, email="coord@test.com")
            user = await _seed_user(eng, email="user@test.com")
            role = await _seed_role(eng, permissions=["tareas:gestionar"])
            await _assign_role(eng, coord.id, role.id)
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(coord.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            tarea = await _seed_tarea(eng, asignado_a=user.id, asignado_por=coord.id,
                                      estado=EstadoTarea.RESUELTA)
            async with await _make_app() as client:
                response = await client.patch(
                    f"/api/tareas/{tarea.id}",
                    json={"estado": "Pendiente"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["estado"] == "Pendiente"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_profesor_no_puede_cancelar(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            prof = await _seed_user(eng, email="prof@test.com")
            role = await _seed_role(eng, permissions=["tareas:gestionar"])
            await _assign_role(eng, prof.id, role.id)
            token = create_access_token(
                {"sub": str(prof.id), "tenant_id": str(TENANT_ID), "roles": ["PROFESOR"]},
            )
            tarea = await _seed_tarea(eng, asignado_a=prof.id, asignado_por=prof.id)
            async with await _make_app() as client:
                response = await client.patch(
                    f"/api/tareas/{tarea.id}",
                    json={"estado": "Cancelada"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 409
        finally:
            await _teardown_db()
            await eng.dispose()


class TestComentarios:
    async def test_agregar_comentario(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["tareas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["PROFESOR"]},
            )
            tarea = await _seed_tarea(eng, asignado_a=user.id, asignado_por=user.id)
            async with await _make_app() as client:
                response = await client.post(
                    f"/api/tareas/{tarea.id}/comentarios",
                    json={"texto": "Un comentario"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 201
            assert response.json()["texto"] == "Un comentario"
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_listar_comentarios(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["tareas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["PROFESOR"]},
            )
            tarea = await _seed_tarea(eng, asignado_a=user.id, asignado_por=user.id)
            await _seed_comentario(eng, tarea_id=tarea.id, autor_id=user.id, texto="Comentario 1")
            await _seed_comentario(eng, tarea_id=tarea.id, autor_id=user.id, texto="Comentario 2")
            async with await _make_app() as client:
                response = await client.get(
                    f"/api/tareas/{tarea.id}/comentarios",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert len(response.json()) == 2
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_comentario_tarea_inexistente_404(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["tareas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["PROFESOR"]},
            )
            async with await _make_app() as client:
                response = await client.post(
                    f"/api/tareas/{uuid.uuid4()}/comentarios",
                    json={"texto": "Comentario"},
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 404
        finally:
            await _teardown_db()
            await eng.dispose()


class TestPermissionGuard:
    async def test_profesor_puede_gestionar(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["tareas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["PROFESOR"]},
            )
            async with await _make_app() as client:
                response = await client.get(
                    "/api/tareas/",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_alumno_no_puede_gestionar(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            alumno = await _seed_user(eng, email="alumno@test.com")
            role = await _seed_role(eng, name="ALUMNO", permissions=[])
            await _assign_role(eng, alumno.id, role.id)
            token = create_access_token(
                {"sub": str(alumno.id), "tenant_id": str(TENANT_ID), "roles": ["ALUMNO"]},
            )
            async with await _make_app() as client:
                response = await client.get(
                    "/api/tareas/",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 403
        finally:
            await _teardown_db()
            await eng.dispose()


class TestSoftDelete:
    async def test_soft_deleted_excluded_from_list(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["tareas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            tarea = await _seed_tarea(eng, asignado_a=user.id, asignado_por=user.id)
            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from sqlalchemy import update, func
                stmt = update(Tarea).where(Tarea.id == tarea.id).values(deleted_at=func.now())
                await session.execute(stmt)
                await session.commit()
            async with await _make_app() as client:
                response = await client.get(
                    "/api/tareas/admin",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 200
            assert response.json()["total"] == 0
        finally:
            await _teardown_db()
            await eng.dispose()

    async def test_soft_deleted_detail_returns_404(self):
        eng = create_async_engine(DB_URL, echo=False)
        try:
            await _setup_db()
            await _seed_tenant(eng)
            user = await _seed_user(eng)
            role = await _seed_role(eng, permissions=["tareas:gestionar"])
            await _assign_role(eng, user.id, role.id)
            token = create_access_token(
                {"sub": str(user.id), "tenant_id": str(TENANT_ID), "roles": ["COORDINADOR"]},
            )
            tarea = await _seed_tarea(eng, asignado_a=user.id, asignado_por=user.id)
            factory = async_sessionmaker(eng, expire_on_commit=False)
            async with factory() as session:
                from sqlalchemy import update, func
                stmt = update(Tarea).where(Tarea.id == tarea.id).values(deleted_at=func.now())
                await session.execute(stmt)
                await session.commit()
            async with await _make_app() as client:
                response = await client.get(
                    f"/api/tareas/{tarea.id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
            assert response.status_code == 404
        finally:
            await _teardown_db()
            await eng.dispose()
