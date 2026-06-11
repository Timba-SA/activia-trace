"""Seed script: creates a default tenant, ADMIN role, and test user.

Usage:
    docker compose exec api python -m app.seed
"""

import asyncio
import uuid

from sqlalchemy import text

from app.core.database import get_factory
from app.core.security import hash_password
from app.models.role import Role
from app.models.usuario import Usuario
from app.models.usuario_role import UsuarioRole
from app.repositories.role_repository import UsuarioRoleRepository

# ── Test credentials ──────────────────────────────────────────────────
TEST_EMAIL = "admin@activia-trace.com"
TEST_PASSWORD = "admin123"

# All permissions in the system
ALL_PERMISSIONS = [
    "atrasados:ver",
    "auditoria:ver",
    "avisos:publicar",
    "calificaciones:configurar-umbral",
    "calificaciones:importar",
    "coloquios:gestionar",
    "coloquios:reservar",
    "coloquios:ver",
    "comunicacion:aprobar",
    "comunicacion:enviar",
    "encuentros:gestionar",
    "encuentros:ver",
    "equipos:asignar",
    "equipos:ver",
    "estructura:gestionar",
    "guardias:registrar",
    "guardias:ver",
    "impersonacion:usar",
    "liquidaciones:calcular",
    "liquidaciones:cerrar",
    "liquidaciones:configurar-salarios",
    "liquidaciones:exportar",
    "liquidaciones:gestionar-facturas",
    "liquidaciones:ver",
    "padron:cargar",
    "programas:gestionar",
    "programas:ver",
    "roles:gestionar",
    "tareas:gestionar",
    "usuarios:asignar",
    "usuarios:gestionar",
]

# Deterministic UUIDs for the seed entities
SEED_TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
SEED_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000010")
SEED_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000100")


async def seed():
    factory = get_factory()
    async with factory() as session:
        # ── 1. Tenant (raw SQL to avoid ORM column mismatch) ────────
        result = await session.execute(
            text("SELECT id FROM tenant WHERE id = :id"),
            {"id": SEED_TENANT_ID},
        )
        tenant_exists = result.scalar() is not None

        if not tenant_exists:
            await session.execute(
                text("""
                    INSERT INTO tenant (id, name, slug, code, is_active, created_at, updated_at)
                    VALUES (:id, :name, :slug, :code, true, NOW(), NOW())
                """),
                {
                    "id": SEED_TENANT_ID,
                    "name": "Activia Trace (Default)",
                    "slug": "activia",
                    "code": "ACT",
                },
            )
            await session.flush()
            print(f"✅ Tenant created: Activia Trace (Default) — slug=activia")
        else:
            print(f"ℹ️  Tenant already exists (id={SEED_TENANT_ID})")

        # ── 2. ADMIN role ────────────────────────────────────────────
        result = await session.execute(
            text("SELECT id FROM role WHERE id = :id"),
            {"id": SEED_ROLE_ID},
        )
        role_exists = result.scalar() is not None

        if not role_exists:
            role = Role(
                id=SEED_ROLE_ID,
                tenant_id=SEED_TENANT_ID,
                name="ADMIN",
                description="System administrator with all permissions",
                permissions=ALL_PERMISSIONS,
                is_system_role=True,
            )
            session.add(role)
            await session.flush()
            print(f"✅ Role created: ADMIN ({len(ALL_PERMISSIONS)} permissions)")
        else:
            print(f"ℹ️  Role ADMIN already exists")

        # ── 3. Test user ─────────────────────────────────────────────
        result = await session.execute(
            text("SELECT id FROM usuario WHERE id = :id"),
            {"id": SEED_USER_ID},
        )
        user_exists = result.scalar() is not None

        if not user_exists:
            hashed = hash_password(TEST_PASSWORD)
            user = Usuario(
                id=SEED_USER_ID,
                tenant_id=SEED_TENANT_ID,
                email=TEST_EMAIL,
                hashed_password=hashed,
                is_active=True,
                is_2fa_enabled=False,
                nombre="Admin",
                apellido="Trace",
            )
            session.add(user)
            await session.flush()
            print(f"✅ User created: {TEST_EMAIL} / {TEST_PASSWORD}")
        else:
            print(f"ℹ️  User {TEST_EMAIL} already exists")

        # ── 4. Assign role ───────────────────────────────────────────
        role_repo = UsuarioRoleRepository(session, SEED_TENANT_ID)
        already_assigned = await role_repo.has_assignment(SEED_USER_ID, SEED_ROLE_ID)
        if not already_assigned:
            assignment = UsuarioRole(
                usuario_id=SEED_USER_ID,
                role_id=SEED_ROLE_ID,
                tenant_id=SEED_TENANT_ID,
            )
            session.add(assignment)
            await session.flush()
            print(f"✅ Role ADMIN assigned to {TEST_EMAIL}")
        else:
            print(f"ℹ️  Role already assigned to user")

        await session.commit()

    print("\n🎉 Seed complete! You can now log in with:")
    print(f"   Email:    {TEST_EMAIL}")
    print(f"   Password: {TEST_PASSWORD}")
    print(f"   Tenant slug: activia")


if __name__ == "__main__":
    asyncio.run(seed())
