"""Seed test admin users for auth development.

Usage:
    python -m scripts.seed_auth

Creates a tenant and an admin@test.com user for each tenant.
Seeds the 7 system roles if missing, and assigns ADMIN to admin@test.com.
Safe to re-run (idempotent via uniqueness checks).
"""

import asyncio
import os
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://active_trace:active_trace@localhost:5432/active_trace")

from app.core.security import hash_password
from app.models.role import Role
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.models.usuario_role import UsuarioRole

SYSTEM_ROLES = {
    "ALUMNO": {
        "description": "Estudiante que cursa materias",
        "permissions": [
            "academico:ver_estado_propio",
            "evaluaciones:reservar",
            "comunicacion:confirmar_avisos",
        ],
    },
    "TUTOR": {
        "description": "Auxiliar / ayudante de cátedra",
        "permissions": [
            "comunicacion:confirmar_avisos",
            "atrasados:ver",
            "entregas:detectar_sin_corregir",
            "encuentros:gestionar",
            "guardias:registrar",
        ],
    },
    "PROFESOR": {
        "description": "Docente a cargo de una o más comisiones",
        "permissions": [
            "comunicacion:confirmar_avisos",
            "calificaciones:importar",
            "calificaciones:configurar-umbral",
            "atrasados:ver",
            "entregas:detectar_sin_corregir",
            "comunicacion:enviar",
            "encuentros:gestionar",
            "guardias:registrar",
            "tareas:gestionar",
        ],
    },
    "COORDINADOR": {
        "description": "Responsable de un conjunto de materias o de una cohorte",
        "permissions": [
            "comunicacion:confirmar_avisos",
            "calificaciones:importar",
            "calificaciones:configurar-umbral",
            "atrasados:ver",
            "entregas:detectar_sin_corregir",
            "comunicacion:enviar",
            "comunicacion:aprobar_masivas",
            "encuentros:gestionar",
            "guardias:registrar",
            "tareas:gestionar",
            "avisos:publicar",
            "equipos:gestionar",
            "auditoria:ver",
            "padron:cargar",
        ],
    },
    "NEXO": {
        "description": "Rol de articulación / enlace transversal",
        "permissions": [
            "comunicacion:confirmar_avisos",
            "atrasados:ver",
            "entregas:detectar_sin_corregir",
            "comunicacion:enviar",
            "encuentros:gestionar",
            "avisos:publicar",
            "auditoria:ver",
        ],
    },
    "ADMIN": {
        "description": "Administrador del sistema dentro del tenant",
        "permissions": [
            "comunicacion:confirmar_avisos",
            "calificaciones:importar",
            "calificaciones:configurar-umbral",
            "atrasados:ver",
            "entregas:detectar_sin_corregir",
            "comunicacion:enviar",
            "comunicacion:aprobar_masivas",
            "encuentros:gestionar",
            "guardias:registrar",
            "tareas:gestionar",
            "avisos:publicar",
            "equipos:gestionar",
            "estructura:gestionar",
            "usuarios:gestionar",
            "auditoria:ver",
            "tenant:configurar",
            "roles:gestionar",
            "padron:cargar",
        ],
    },
    "FINANZAS": {
        "description": "Responsable de liquidaciones y honorarios",
        "permissions": [
            "comunicacion:confirmar_avisos",
            "auditoria:ver",
            "liquidaciones:grilla_salarial",
            "liquidaciones:calcular_cerrar",
            "liquidaciones:facturas",
        ],
    },
}


async def seed():
    db_url = os.environ["DATABASE_URL"]
    engine = create_async_engine(db_url, echo=False)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as session:
        result = await session.execute(select(Tenant))
        tenants = result.scalars().all()

        if not tenants:
            tenant_id = uuid.uuid4()
            tenant = Tenant(
                id=tenant_id,
                name="Default Tenant",
                slug="default",
                code="DEF",
            )
            session.add(tenant)
            await session.flush()
            tenants = [tenant]

        for tenant in tenants:
            await _seed_roles_for_tenant(session, tenant.id)

            existing = await session.execute(
                select(Usuario).where(
                    Usuario.tenant_id == tenant.id,
                    Usuario.email == "admin@test.com",
                )
            )
            user = existing.scalars().first()

            if user is None:
                user = Usuario(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    email="admin@test.com",
                    hashed_password=hash_password("admin123"),
                    is_active=True,
                )
                session.add(user)
                await session.flush()
                print(f"[OK] Created admin@test.com in tenant {tenant.slug} (id={user.id})")
            else:
                print(f"[SKIP] admin@test.com already exists in tenant {tenant.slug}")

            admin_role = await session.execute(
                select(Role).where(
                    Role.tenant_id == tenant.id,
                    Role.name == "ADMIN",
                )
            )
            admin_role = admin_role.scalars().first()

            if admin_role is not None:
                already_assigned = await session.execute(
                    select(UsuarioRole).where(
                        UsuarioRole.usuario_id == user.id,
                        UsuarioRole.role_id == admin_role.id,
                    )
                )
                if not already_assigned.scalars().first():
                    session.add(UsuarioRole(
                        usuario_id=user.id,
                        role_id=admin_role.id,
                        tenant_id=tenant.id,
                    ))
                    print(f"[OK] Assigned ADMIN role to admin@test.com in tenant {tenant.slug}")

        await session.commit()

    await engine.dispose()


async def _seed_roles_for_tenant(session, tenant_id):
    for role_name, role_data in SYSTEM_ROLES.items():
        existing = (
            await session.execute(
                select(Role).where(
                    Role.tenant_id == tenant_id,
                    Role.name == role_name,
                )
            )
        ).scalars().first()
        if existing:
            continue
        role = Role(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name=role_name,
            description=role_data["description"],
            permissions=role_data["permissions"],
            is_system_role=True,
        )
        session.add(role)
        print(f"[OK] Created role {role_name} for tenant {tenant_id}")


if __name__ == "__main__":
    asyncio.run(seed())
