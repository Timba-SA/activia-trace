"""Seed test data via raw SQL - bypass ORM model mismatches."""
import uuid
from datetime import date, time
from sqlalchemy import text
from app.core.database import get_factory
import asyncio

TENANT_ID = "00000000-0000-0000-0000-000000000001"
CARRERA_ID = "00000000-0000-0000-0000-000000000200"
COHORTE_ID = "00000000-0000-0000-0000-000000000300"
MATERIA_ID = "00000000-0000-0000-0000-000000000400"
SLOT_LUNES = "00000000-0000-0000-0000-000000000500"
SLOT_MIE = "00000000-0000-0000-0000-000000000501"
PROGRAMA_ID = "00000000-0000-0000-0000-000000000600"


async def seed():
    factory = get_factory()
    async with factory() as s:
        # 1. Carrera
        r = await s.execute(text("SELECT id FROM carrera WHERE id = :id"), {"id": CARRERA_ID})
        if not r.scalar():
            await s.execute(text("""
                INSERT INTO carrera (id, tenant_id, nombre, codigo, is_active, created_at, updated_at)
                VALUES (:id, :tid, 'Ingeniería en Sistemas', 'IS-2023', true, NOW(), NOW())
            """), {"id": CARRERA_ID, "tid": TENANT_ID})
            print("✅ Carrera")

        # 2. Cohorte
        r = await s.execute(text("SELECT id FROM cohorte WHERE id = :id"), {"id": COHORTE_ID})
        if not r.scalar():
            await s.execute(text("""
                INSERT INTO cohorte (id, tenant_id, carrera_id, nombre, anio, is_active, created_at, updated_at)
                VALUES (:id, :tid, :cid, '2023-1', 2023, true, NOW(), NOW())
            """), {"id": COHORTE_ID, "tid": TENANT_ID, "cid": CARRERA_ID})
            print("✅ Cohorte")

        # 3. Materia
        r = await s.execute(text("SELECT id FROM materia WHERE id = :id"), {"id": MATERIA_ID})
        if not r.scalar():
            await s.execute(text("""
                INSERT INTO materia (id, tenant_id, carrera_id, nombre, codigo, carga_horaria, is_active, created_at, updated_at)
                VALUES (:id, :tid, :cid, 'Análisis de Sistemas II', 'ASI-2023', 120, true, NOW(), NOW())
            """), {"id": MATERIA_ID, "tid": TENANT_ID, "cid": CARRERA_ID})
            print("✅ Materia")

        # 4. Slot encuentro (uses dia_semana enum 'Lunes')
        r = await s.execute(text("SELECT id FROM slot_encuentro WHERE id = :id"), {"id": SLOT_LUNES})
        if not r.scalar():
            await s.execute(text("""
                INSERT INTO slot_encuentro (id, tenant_id, materia_id, dia_semana, hora, titulo, fecha_inicio, cant_semanas, vig_desde, vig_hasta, created_at, updated_at)
                VALUES (:id1, :tid, :mid, 'Lunes'::dia_semana, '08:00'::time, 'Teoría Lunes', '2023-03-01', 16, '2023-03-01', '2023-07-15', NOW(), NOW())
            """), {"id1": SLOT_LUNES, "tid": TENANT_ID, "mid": MATERIA_ID})
            await s.execute(text("""
                INSERT INTO slot_encuentro (id, tenant_id, materia_id, dia_semana, hora, titulo, fecha_inicio, cant_semanas, vig_desde, vig_hasta, created_at, updated_at)
                VALUES (:id2, :tid, :mid, 'Miercoles'::dia_semana, '10:00'::time, 'Práctica Miércoles', '2023-03-01', 16, '2023-03-01', '2023-07-15', NOW(), NOW())
            """), {"id2": SLOT_MIE, "tid": TENANT_ID, "mid": MATERIA_ID})
            print("✅ Slots encuentro")

        # 5. Programa materia
        r = await s.execute(text("SELECT id FROM programa_materia WHERE id = :id"), {"id": PROGRAMA_ID})
        if not r.scalar():
            await s.execute(text("""
                INSERT INTO programa_materia (id, tenant_id, materia_id, cohorte_id, nombre, activo, created_at, updated_at)
                VALUES (:id, :tid, :mid, :coid, 'Análisis de Sistemas II - 2023-1', true, NOW(), NOW())
            """), {"id": PROGRAMA_ID, "tid": TENANT_ID, "mid": MATERIA_ID, "coid": COHORTE_ID})
            print("✅ Programa materia")

        await s.commit()
    print("\n🎉 Datos de prueba listos!")


if __name__ == "__main__":
    asyncio.run(seed())
