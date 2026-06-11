"""Fix missing columns in the database schema.

alembic_version says 017 but intermediate migrations were not applied.
"""
import asyncio
from app.core.database import get_factory
from sqlalchemy import text

MISSING_COLUMNS = [
    # Migration 005: add columns to usuario
    ("usuario", "nombre", "VARCHAR(255)"),
    ("usuario", "apellido", "VARCHAR(255)"),
    ("usuario", "dni", "TEXT"),
    ("usuario", "cuil", "TEXT"),
    ("usuario", "telefono", "VARCHAR(50)"),
    ("usuario", "direccion", "VARCHAR(500)"),
    ("usuario", "fecha_nacimiento", "DATE"),
    ("usuario", "legajo", "VARCHAR(50)"),
    ("usuario", "cbu", "TEXT"),
    # Migration 008: add column to tenant
    ("tenant", "aprobacion_comunicaciones_requerida", "BOOLEAN NOT NULL DEFAULT false"),
]


async def fix():
    factory = get_factory()
    async with factory() as session:
        for table, column, col_type in MISSING_COLUMNS:
            # Check if column exists
            result = await session.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = :table AND column_name = :column"
                ),
                {"table": table, "column": column},
            )
            if result.scalar() is None:
                print(f"➕ Adding {table}.{column} ({col_type})")
                await session.execute(
                    text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
                )
            else:
                print(f"✅ {table}.{column} already exists")

        # Also add the unique constraint from migration 005
        try:
            await session.execute(
                text(
                    "ALTER TABLE usuario "
                    "ADD CONSTRAINT uq_usuario_legajo_tenant "
                    "UNIQUE (tenant_id, legajo)"
                )
            )
            print("➕ Added unique constraint uq_usuario_legajo_tenant")
        except Exception:
            print("ℹ️  Unique constraint already exists (or legajo is nullable)")

        await session.commit()

    print("\n✅ Schema fixed! Now run the seed to create test data.")


if __name__ == "__main__":
    asyncio.run(fix())
