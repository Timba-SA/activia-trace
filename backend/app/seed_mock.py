"""Mock seed: populates the DB with realistic demo data for end-to-end testing.

Run AFTER `python -m app.seed` (which creates the tenant, ADMIN role, and admin user).

Usage:
    docker compose exec api python -m app.seed_mock
"""

import asyncio
import uuid
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import text

from app.core.database import get_factory
from app.core.security import hash_password
from app.models.role import Role
from app.models.usuario import Usuario
from app.models.usuario_role import UsuarioRole
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.models.asignacion import Asignacion
from app.models.encuentro_slot import SlotEncuentro, DiaSemana
from app.models.encuentro_instancia import InstanciaEncuentro, EstadoInstancia
from app.models.guardia import Guardia, EstadoGuardia, DiaSemanaGuardia
from app.models.evaluacion import Evaluacion, TipoEvaluacion
from app.models.turno_disponible import TurnoDisponible
from app.models.reserva_evaluacion import ReservaEvaluacion, EstadoReserva
from app.models.resultado_evaluacion import ResultadoEvaluacion
from app.models.tarea import Tarea, EstadoTarea
from app.models.comentario_tarea import ComentarioTarea
from app.models.aviso import Aviso, AlcanceAviso, SeveridadAviso
from app.models.umbral_materia import UmbralMateria
from app.models.salario_base import SalarioBase
from app.repositories.role_repository import UsuarioRoleRepository

# ── Deterministic UUIDs ───────────────────────────────────────────────
TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

# Carreras
CARRERA_SIS_ID = uuid.UUID("00000000-0000-0000-0000-000000000201")
CARRERA_CONT_ID = uuid.UUID("00000000-0000-0000-0000-000000000202")

# Cohortes
COHORTE_SIS_ID = uuid.UUID("00000000-0000-0000-0000-000000000301")
COHORTE_CONT_ID = uuid.UUID("00000000-0000-0000-0000-000000000302")

# Materias
MATERIA_PROG1_ID = uuid.UUID("00000000-0000-0000-0000-000000000401")
MATERIA_BD_ID = uuid.UUID("00000000-0000-0000-0000-000000000402")
MATERIA_ISW_ID = uuid.UUID("00000000-0000-0000-0000-000000000403")

# Roles
ROLE_PROFESOR_ID = uuid.UUID("00000000-0000-0000-0000-000000000501")
ROLE_TUTOR_ID = uuid.UUID("00000000-0000-0000-0000-000000000502")
ROLE_ALUMNO_ID = uuid.UUID("00000000-0000-0000-0000-000000000503")

# Usuarios
USER_PROFESOR_ID = uuid.UUID("00000000-0000-0000-0000-000000000601")
USER_TUTOR_ID = uuid.UUID("00000000-0000-0000-0000-000000000602")
USER_ALUMNO1_ID = uuid.UUID("00000000-0000-0000-0000-000000000603")
USER_ALUMNO2_ID = uuid.UUID("00000000-0000-0000-0000-000000000604")

# Asignaciones
ASIG_PROFESOR_PROG1_ID = uuid.UUID("00000000-0000-0000-0000-000000000701")
ASIG_TUTOR_PROG1_ID = uuid.UUID("00000000-0000-0000-0000-000000000702")
ASIG_ALUMNO1_ID = uuid.UUID("00000000-0000-0000-0000-000000000703")
ASIG_ALUMNO2_ID = uuid.UUID("00000000-0000-0000-0000-000000000704")

# Slots
SLOT_LUNES_ID = uuid.UUID("00000000-0000-0000-0000-000000000801")
SLOT_MIERCOLES_ID = uuid.UUID("00000000-0000-0000-0000-000000000802")

# Instancias
INSTANCIA_1_ID = uuid.UUID("00000000-0000-0000-0000-000000000901")
INSTANCIA_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000902")
INSTANCIA_3_ID = uuid.UUID("00000000-0000-0000-0000-000000000903")
INSTANCIA_4_ID = uuid.UUID("00000000-0000-0000-0000-000000000904")
INSTANCIA_5_ID = uuid.UUID("00000000-0000-0000-0000-000000000905")

# Guardias
GUARDIA_1_ID = uuid.UUID("00000000-0000-0000-0000-000000001001")
GUARDIA_2_ID = uuid.UUID("00000000-0000-0000-0000-000000001002")
GUARDIA_3_ID = uuid.UUID("00000000-0000-0000-0000-000000001003")

# Evaluaciones
EVAL_PARCIAL1_ID = uuid.UUID("00000000-0000-0000-0000-000000001101")
EVAL_PARCIAL2_ID = uuid.UUID("00000000-0000-0000-0000-000000001102")
EVAL_COLOQUIO_ID = uuid.UUID("00000000-0000-0000-0000-000000001103")
EVAL_TP1_ID = uuid.UUID("00000000-0000-0000-0000-000000001104")

# Turnos
TURNO_1_ID = uuid.UUID("00000000-0000-0000-0000-000000001201")
TURNO_2_ID = uuid.UUID("00000000-0000-0000-0000-000000001202")
TURNO_3_ID = uuid.UUID("00000000-0000-0000-0000-000000001203")

# Reservas
RESERVA_1_ID = uuid.UUID("00000000-0000-0000-0000-000000001301")

# Resultados
RESULTADO_1_ID = uuid.UUID("00000000-0000-0000-0000-000000001401")

# Tareas
TAREA_1_ID = uuid.UUID("00000000-0000-0000-0000-000000001501")
TAREA_2_ID = uuid.UUID("00000000-0000-0000-0000-000000001502")

# Comentarios
COMENTARIO_1_ID = uuid.UUID("00000000-0000-0000-0000-000000001601")

# Avisos
AVISO_1_ID = uuid.UUID("00000000-0000-0000-0000-000000001701")
AVISO_2_ID = uuid.UUID("00000000-0000-0000-0000-000000001702")

# Umbrales
UMBRAL_PROG1_ID = uuid.UUID("00000000-0000-0000-0000-000000001801")

# Salarios
SALARIO_PROF_ID = uuid.UUID("00000000-0000-0000-0000-000000001901")
SALARIO_TUT_ID = uuid.UUID("00000000-0000-0000-0000-000000001902")
SALARIO_NEXO_ID = uuid.UUID("00000000-0000-0000-0000-000000001903")

# ── Common password for all mock users ─────────────────────────────────
MOCK_PASSWORD = "123456"

# ── Constants ──────────────────────────────────────────────────────────
TODAY = date.today()
NOW = datetime.now(timezone.utc)

# ── Permission sets by role ───────────────────────────────────────────
PERMISOS_PROFESOR = [
    "encuentros:ver", "encuentros:gestionar",
    "guardias:ver", "guardias:registrar",
    "coloquios:ver", "coloquios:gestionar",
    "coloquios:reservar",
    "tareas:gestionar",
    "calificaciones:importar", "calificaciones:configurar-umbral",
    "equipos:ver", "equipos:asignar",
    "programas:ver", "programas:gestionar",
    "atrasados:ver",
    "comunicacion:enviar",
    "avisos:publicar",
]

PERMISOS_TUTOR = [
    "encuentros:ver",
    "guardias:ver",
    "coloquios:ver",
    "tareas:gestionar",
    "atrasados:ver",
    "comunicacion:enviar",
]

PERMISOS_ALUMNO = [
    "encuentros:ver",
    "coloquios:ver",
    "coloquios:reservar",
    "atrasados:ver",
]


# ── Helper ─────────────────────────────────────────────────────────────
async def id_exists(session, table_name: str, id_val: uuid.UUID) -> bool:
    result = await session.execute(
        text(f"SELECT id FROM {table_name} WHERE id = :id"),
        {"id": id_val},
    )
    return result.scalar() is not None


# ── Seed function ──────────────────────────────────────────────────────
async def seed_mock():
    factory = get_factory()
    hashed = hash_password(MOCK_PASSWORD)

    async with factory() as session:
        # ═══════════════════════════════════════════════════════════════
        # 1. CARRERAS
        # ═══════════════════════════════════════════════════════════════
        if not await id_exists(session, "carrera", CARRERA_SIS_ID):
            session.add(Carrera(
                id=CARRERA_SIS_ID,
                tenant_id=TENANT_ID,
                codigo="SIS",
                nombre="Licenciatura en Sistemas",
                descripcion="Carrera de grado en Sistemas de Información",
                duracion_anios=4,
                is_active=True,
            ))
            await session.flush()
            print("✅ Carrera: Licenciatura en Sistemas")
        else:
            print("ℹ️  Carrera SIS ya existe")

        if not await id_exists(session, "carrera", CARRERA_CONT_ID):
            session.add(Carrera(
                id=CARRERA_CONT_ID,
                tenant_id=TENANT_ID,
                codigo="CONT",
                nombre="Contador Público",
                descripcion="Carrera de grado en Contabilidad",
                duracion_anios=5,
                is_active=True,
            ))
            await session.flush()
            print("✅ Carrera: Contador Público")
        else:
            print("ℹ️  Carrera CONT ya existe")

        # ═══════════════════════════════════════════════════════════════
        # 2. COHORTES
        # ═══════════════════════════════════════════════════════════════
        if not await id_exists(session, "cohorte", COHORTE_SIS_ID):
            session.add(Cohorte(
                id=COHORTE_SIS_ID,
                tenant_id=TENANT_ID,
                carrera_id=CARRERA_SIS_ID,
                nombre=f"1er Año {TODAY.year}",
                anio=TODAY.year,
                is_active=True,
            ))
            await session.flush()
            print(f"✅ Cohorte SIS: 1er Año {TODAY.year}")
        else:
            print("ℹ️  Cohorte SIS ya existe")

        if not await id_exists(session, "cohorte", COHORTE_CONT_ID):
            session.add(Cohorte(
                id=COHORTE_CONT_ID,
                tenant_id=TENANT_ID,
                carrera_id=CARRERA_CONT_ID,
                nombre=f"1er Año {TODAY.year}",
                anio=TODAY.year,
                is_active=True,
            ))
            await session.flush()
            print(f"✅ Cohorte CONT: 1er Año {TODAY.year}")
        else:
            print("ℹ️  Cohorte CONT ya existe")

        # ═══════════════════════════════════════════════════════════════
        # 3. MATERIAS
        # ═══════════════════════════════════════════════════════════════
        for mid, cod, nom, ch in [
            (MATERIA_PROG1_ID, "PROG1", "Programación I", 128),
            (MATERIA_BD_ID, "BD", "Base de Datos", 96),
            (MATERIA_ISW_ID, "ISW", "Ingeniería de Software", 96),
        ]:
            if not await id_exists(session, "materia", mid):
                session.add(Materia(
                    id=mid, tenant_id=TENANT_ID, carrera_id=CARRERA_SIS_ID,
                    codigo=cod, nombre=nom, carga_horaria=ch, is_active=True,
                ))
                await session.flush()
                print(f"✅ Materia: {nom} ({cod})")
            else:
                print(f"ℹ️  Materia {cod} ya existe")

        # ═══════════════════════════════════════════════════════════════
        # 4. ROLES docentes
        # ═══════════════════════════════════════════════════════════════
        for rid, rname, rdesc, perms in [
            (ROLE_PROFESOR_ID, "PROFESOR", "Docente a cargo de materias", PERMISOS_PROFESOR),
            (ROLE_TUTOR_ID, "TUTOR", "Asistente docente de apoyo", PERMISOS_TUTOR),
            (ROLE_ALUMNO_ID, "ALUMNO", "Estudiante", PERMISOS_ALUMNO),
        ]:
            if not await id_exists(session, "role", rid):
                session.add(Role(
                    id=rid, tenant_id=TENANT_ID, name=rname,
                    description=rdesc, permissions=perms, is_system_role=False,
                ))
                await session.flush()
                print(f"✅ Rol: {rname} ({len(perms)} permisos)")
            else:
                print(f"ℹ️  Rol {rname} ya existe")

        # ═══════════════════════════════════════════════════════════════
        # 5. USUARIOS
        # ═══════════════════════════════════════════════════════════════
        for uid, uemail, unombre, uapellido, _ in [
            (USER_PROFESOR_ID, "profesor@activia-trace.com", "Carlos", "García", "PROFESOR"),
            (USER_TUTOR_ID, "tutor@activia-trace.com", "María", "López", "TUTOR"),
            (USER_ALUMNO1_ID, "alumno1@activia-trace.com", "Juan", "Pérez", "ALUMNO"),
            (USER_ALUMNO2_ID, "alumno2@activia-trace.com", "Ana", "Rodríguez", "ALUMNO"),
        ]:
            if not await id_exists(session, "usuario", uid):
                session.add(Usuario(
                    id=uid, tenant_id=TENANT_ID, email=uemail,
                    hashed_password=hashed, is_active=True, is_2fa_enabled=False,
                    nombre=unombre, apellido=uapellido,
                ))
                await session.flush()
                print(f"✅ Usuario: {uemail} / {MOCK_PASSWORD}")
            else:
                print(f"ℹ️  Usuario {uemail} ya existe")

        # ═══════════════════════════════════════════════════════════════
        # 6. ASIGNACIONES
        # ═══════════════════════════════════════════════════════════════
        if not await id_exists(session, "asignacion", ASIG_PROFESOR_PROG1_ID):
            session.add(Asignacion(
                id=ASIG_PROFESOR_PROG1_ID, tenant_id=TENANT_ID,
                usuario_id=USER_PROFESOR_ID, rol="PROFESOR",
                carrera_id=CARRERA_SIS_ID, materia_id=MATERIA_PROG1_ID,
                cohorte_id=COHORTE_SIS_ID,
                fecha_inicio=date(TODAY.year, 3, 1),
                fecha_fin=date(TODAY.year, 12, 31),
                comisiones=["COM-A", "COM-B"], is_active=True,
            ))
            await session.flush()
            print("✅ Asignación: Carlos García → Programación I (PROFESOR)")
        else:
            print("ℹ️  Asignación PROFESOR_PROG1 ya existe")

        if not await id_exists(session, "asignacion", ASIG_TUTOR_PROG1_ID):
            session.add(Asignacion(
                id=ASIG_TUTOR_PROG1_ID, tenant_id=TENANT_ID,
                usuario_id=USER_TUTOR_ID, rol="TUTOR",
                carrera_id=CARRERA_SIS_ID, materia_id=MATERIA_PROG1_ID,
                cohorte_id=COHORTE_SIS_ID, responsable_id=USER_PROFESOR_ID,
                fecha_inicio=date(TODAY.year, 3, 1),
                fecha_fin=date(TODAY.year, 12, 31),
                comisiones=["COM-A", "COM-B"], is_active=True,
            ))
            await session.flush()
            print("✅ Asignación: María López → Programación I (TUTOR)")
        else:
            print("ℹ️  Asignación TUTOR_PROG1 ya existe")

        if not await id_exists(session, "asignacion", ASIG_ALUMNO1_ID):
            session.add(Asignacion(
                id=ASIG_ALUMNO1_ID, tenant_id=TENANT_ID,
                usuario_id=USER_ALUMNO1_ID, rol="ALUMNO",
                carrera_id=CARRERA_SIS_ID, materia_id=MATERIA_PROG1_ID,
                cohorte_id=COHORTE_SIS_ID,
                fecha_inicio=date(TODAY.year, 3, 1),
                comisiones=["COM-A"], is_active=True,
            ))
            await session.flush()
            print("✅ Asignación: Juan Pérez → Programación I (ALUMNO)")
        else:
            print("ℹ️  Asignación ALUMNO1 ya existe")

        if not await id_exists(session, "asignacion", ASIG_ALUMNO2_ID):
            session.add(Asignacion(
                id=ASIG_ALUMNO2_ID, tenant_id=TENANT_ID,
                usuario_id=USER_ALUMNO2_ID, rol="ALUMNO",
                carrera_id=CARRERA_SIS_ID, materia_id=MATERIA_PROG1_ID,
                cohorte_id=COHORTE_SIS_ID,
                fecha_inicio=date(TODAY.year, 3, 1),
                comisiones=["COM-A"], is_active=True,
            ))
            await session.flush()
            print("✅ Asignación: Ana Rodríguez → Programación I (ALUMNO)")
        else:
            print("ℹ️  Asignación ALUMNO2 ya existe")

        # ── Role assignments ──────────────────────────────────────────
        role_repo = UsuarioRoleRepository(session, TENANT_ID)
        for uid, rid in [
            (USER_PROFESOR_ID, ROLE_PROFESOR_ID),
            (USER_TUTOR_ID, ROLE_TUTOR_ID),
            (USER_ALUMNO1_ID, ROLE_ALUMNO_ID),
            (USER_ALUMNO2_ID, ROLE_ALUMNO_ID),
        ]:
            if not await role_repo.has_assignment(uid, rid):
                session.add(UsuarioRole(usuario_id=uid, role_id=rid, tenant_id=TENANT_ID))
                await session.flush()
        print("✅ Roles asignados a usuarios")

        # ═══════════════════════════════════════════════════════════════
        # 7. SLOTS de encuentro
        # ═══════════════════════════════════════════════════════════════
        vig_desde = date(TODAY.year, 3, 1)
        vig_hasta = date(TODAY.year, 7, 31)

        if not await id_exists(session, "slot_encuentro", SLOT_LUNES_ID):
            session.add(SlotEncuentro(
                id=SLOT_LUNES_ID, tenant_id=TENANT_ID,
                asignacion_id=ASIG_PROFESOR_PROG1_ID,
                materia_id=MATERIA_PROG1_ID,
                titulo="Programación I — Lunes",
                hora=time(18, 0),
                dia_semana=DiaSemana.LUNES,
                fecha_inicio=vig_desde, cant_semanas=20,
                meet_url="https://meet.google.com/abc-defg-hij",
                vig_desde=vig_desde, vig_hasta=vig_hasta,
            ))
            await session.flush()
            print("✅ Slot: Programación I — Lunes 18:00")
        else:
            print("ℹ️  Slot LUNES ya existe")

        if not await id_exists(session, "slot_encuentro", SLOT_MIERCOLES_ID):
            session.add(SlotEncuentro(
                id=SLOT_MIERCOLES_ID, tenant_id=TENANT_ID,
                asignacion_id=ASIG_PROFESOR_PROG1_ID,
                materia_id=MATERIA_PROG1_ID,
                titulo="Programación I — Miércoles",
                hora=time(18, 0),
                dia_semana=DiaSemana.MIERCOLES,
                fecha_inicio=vig_desde, cant_semanas=20,
                meet_url="https://meet.google.com/abc-defg-hij",
                vig_desde=vig_desde, vig_hasta=vig_hasta,
            ))
            await session.flush()
            print("✅ Slot: Programación I — Miércoles 18:00")
        else:
            print("ℹ️  Slot MIERCOLES ya existe")

        # ═══════════════════════════════════════════════════════════════
        # 8. INSTANCIAS de encuentro (5 variadas)
        # ═══════════════════════════════════════════════════════════════
        for iid, sid, ifecha, ihora, ititulo, iestado in [
            (INSTANCIA_1_ID, SLOT_LUNES_ID, TODAY - timedelta(days=6), time(18, 0),
             "Introducción a la Programación", EstadoInstancia.REALIZADO),
            (INSTANCIA_2_ID, SLOT_MIERCOLES_ID, TODAY - timedelta(days=4), time(18, 0),
             "Variables y Tipos de Datos", EstadoInstancia.REALIZADO),
            (INSTANCIA_3_ID, SLOT_LUNES_ID, TODAY - timedelta(days=2), time(18, 0),
             "Estructuras de Control", EstadoInstancia.REALIZADO),
            (INSTANCIA_4_ID, SLOT_MIERCOLES_ID, TODAY + timedelta(days=2), time(18, 0),
             "Funciones", EstadoInstancia.PROGRAMADO),
            (INSTANCIA_5_ID, SLOT_LUNES_ID, TODAY + timedelta(days=5), time(18, 0),
             "Arreglos y Matrices", EstadoInstancia.PROGRAMADO),
        ]:
            if not await id_exists(session, "instancia_encuentro", iid):
                session.add(InstanciaEncuentro(
                    id=iid, tenant_id=TENANT_ID, slot_id=sid,
                    materia_id=MATERIA_PROG1_ID, fecha=ifecha, hora=ihora,
                    titulo=ititulo, estado=iestado,
                    meet_url="https://meet.google.com/abc-defg-hij",
                ))
                await session.flush()
        print("✅ 5 instancias de encuentro creadas")

        # ═══════════════════════════════════════════════════════════════
        # 9. GUARDIAS
        # ═══════════════════════════════════════════════════════════════
        for gid, gdia, ghorario, gestado in [
            (GUARDIA_1_ID, DiaSemanaGuardia.VIERNES, "14:00-16:00", EstadoGuardia.REALIZADA),
            (GUARDIA_2_ID, DiaSemanaGuardia.VIERNES, "16:00-18:00", EstadoGuardia.REALIZADA),
            (GUARDIA_3_ID, DiaSemanaGuardia.VIERNES, "18:00-20:00", EstadoGuardia.PENDIENTE),
        ]:
            if not await id_exists(session, "guardia", gid):
                session.add(Guardia(
                    id=gid, tenant_id=TENANT_ID,
                    asignacion_id=ASIG_TUTOR_PROG1_ID,
                    materia_id=MATERIA_PROG1_ID,
                    carrera_id=CARRERA_SIS_ID,
                    cohorte_id=COHORTE_SIS_ID,
                    dia=gdia, horario=ghorario, estado=gestado,
                ))
                await session.flush()
        print("✅ 3 guardias creadas")

        # ═══════════════════════════════════════════════════════════════
        # 10. EVALUACIONES
        # ═══════════════════════════════════════════════════════════════
        for eid, etipo, einstancia in [
            (EVAL_PARCIAL1_ID, TipoEvaluacion.PARCIAL, "1er Parcial"),
            (EVAL_PARCIAL2_ID, TipoEvaluacion.PARCIAL, "2do Parcial"),
            (EVAL_COLOQUIO_ID, TipoEvaluacion.COLOQUIO, "Coloquio Final"),
            (EVAL_TP1_ID, TipoEvaluacion.TP, "TP 1 - Algoritmos"),
        ]:
            if not await id_exists(session, "evaluacion", eid):
                session.add(Evaluacion(
                    id=eid, tenant_id=TENANT_ID,
                    materia_id=MATERIA_PROG1_ID,
                    cohorte_id=COHORTE_SIS_ID,
                    tipo=etipo, instancia=einstancia,
                ))
                await session.flush()
        print("✅ 4 evaluaciones creadas")

        # ═══════════════════════════════════════════════════════════════
        # 11. TURNOS disponibles
        # ═══════════════════════════════════════════════════════════════
        for tid, teval_id, tfecha, thora, tcupo in [
            (TURNO_1_ID, EVAL_PARCIAL1_ID, TODAY + timedelta(days=15), time(18, 0), 30),
            (TURNO_2_ID, EVAL_PARCIAL1_ID, TODAY + timedelta(days=16), time(18, 0), 30),
            (TURNO_3_ID, EVAL_COLOQUIO_ID, TODAY + timedelta(days=45), time(18, 0), 20),
        ]:
            if not await id_exists(session, "turno_disponible", tid):
                session.add(TurnoDisponible(
                    id=tid, tenant_id=TENANT_ID,
                    evaluacion_id=teval_id, fecha=tfecha, hora=thora,
                    cupo_total=tcupo, cupos_restantes=tcupo,
                ))
                await session.flush()
        print("✅ 3 turnos disponibles creados")

        # ═══════════════════════════════════════════════════════════════
        # 12. RESERVA de coloquio
        # ═══════════════════════════════════════════════════════════════
        if not await id_exists(session, "reserva_evaluacion", RESERVA_1_ID):
            session.add(ReservaEvaluacion(
                id=RESERVA_1_ID, tenant_id=TENANT_ID,
                evaluacion_id=EVAL_PARCIAL1_ID,
                alumno_id=USER_ALUMNO1_ID,
                turno_id=TURNO_1_ID,
                fecha_hora=datetime.combine(
                    TODAY + timedelta(days=15), time(18, 0), tzinfo=timezone.utc
                ),
                estado=EstadoReserva.ACTIVA,
            ))
            await session.flush()
            print("✅ Reserva: Juan Pérez → 1er Parcial")
        else:
            print("ℹ️  Reserva ya existe")

        # ═══════════════════════════════════════════════════════════════
        # 13. RESULTADO de evaluación (TP1 ya corregido)
        # ═══════════════════════════════════════════════════════════════
        if not await id_exists(session, "resultado_evaluacion", RESULTADO_1_ID):
            session.add(ResultadoEvaluacion(
                id=RESULTADO_1_ID, tenant_id=TENANT_ID,
                evaluacion_id=EVAL_TP1_ID,
                alumno_id=USER_ALUMNO1_ID,
                nota_final="8",
            ))
            await session.flush()
            print("✅ Resultado: Juan Pérez → TP1 = 8")
        else:
            print("ℹ️  Resultado ya existe")

        # ═══════════════════════════════════════════════════════════════
        # 14. TAREAS
        # ═══════════════════════════════════════════════════════════════
        for tid, testado, tasig_a, tasig_por, tmat, tdesc in [
            (TAREA_1_ID, EstadoTarea.PENDIENTE, USER_TUTOR_ID, USER_PROFESOR_ID,
             MATERIA_PROG1_ID, "Preparar ejercicio de funciones para la clase del miércoles"),
            (TAREA_2_ID, EstadoTarea.EN_PROGRESO, USER_TUTOR_ID, USER_PROFESOR_ID,
             MATERIA_PROG1_ID, "Corregir los TP 1 entregados por los alumnos"),
        ]:
            if not await id_exists(session, "tarea", tid):
                session.add(Tarea(
                    id=tid, tenant_id=TENANT_ID,
                    estado=testado, asignado_a=tasig_a,
                    asignado_por=tasig_por, materia_id=tmat,
                    descripcion=tdesc,
                ))
                await session.flush()
        print("✅ 2 tareas creadas")

        # ═══════════════════════════════════════════════════════════════
        # 15. COMENTARIO en tarea
        # ═══════════════════════════════════════════════════════════════
        if not await id_exists(session, "comentario_tarea", COMENTARIO_1_ID):
            session.add(ComentarioTarea(
                id=COMENTARIO_1_ID, tenant_id=TENANT_ID,
                tarea_id=TAREA_1_ID, autor_id=USER_TUTOR_ID,
                texto="¡Dale! ¿A qué hora lo necesitás?",
            ))
            await session.flush()
            print("✅ Comentario en tarea creado")
        else:
            print("ℹ️  Comentario ya existe")

        # ═══════════════════════════════════════════════════════════════
        # 16. UMBRAL de materia
        # ═══════════════════════════════════════════════════════════════
        if not await id_exists(session, "umbral_materia", UMBRAL_PROG1_ID):
            session.add(UmbralMateria(
                id=UMBRAL_PROG1_ID, tenant_id=TENANT_ID,
                materia_id=MATERIA_PROG1_ID, cohorte_id=COHORTE_SIS_ID,
                umbral_pct=60.0,
                valores_aprobados=["Aprobado", "Promocionado"],
            ))
            await session.flush()
            print("✅ Umbral: Programación I (60%)")
        else:
            print("ℹ️  Umbral PROG1 ya existe")

        # ═══════════════════════════════════════════════════════════════
        # 17. AVISOS
        # ═══════════════════════════════════════════════════════════════
        for aid, aalc, amat, acoh, arol, asev, atit, acuerpo, ainicio, afin, aord in [
            (AVISO_1_ID, AlcanceAviso.GLOBAL, None, None, None,
             SeveridadAviso.INFO, "Bienvenidos al ciclo 2026",
             "Este es el sistema de gestión académica trace. Consultá tu horario y calendario de evaluaciones.",
             NOW - timedelta(days=10), NOW + timedelta(days=60), 1),
            (AVISO_2_ID, AlcanceAviso.POR_MATERIA, MATERIA_PROG1_ID, COHORTE_SIS_ID, None,
             SeveridadAviso.ADVERTENCIA, "Entrega TP 1 - Fecha límite",
             "Recordá que la entrega del Trabajo Práctico 1 vence el viernes. Ver consignas en el programa.",
             NOW - timedelta(days=2), NOW + timedelta(days=7), 2),
        ]:
            if not await id_exists(session, "aviso", aid):
                session.add(Aviso(
                    id=aid, tenant_id=TENANT_ID,
                    alcance=aalc, materia_id=amat, cohorte_id=acoh,
                    rol_destino=arol, severidad=asev,
                    titulo=atit, cuerpo=acuerpo,
                    inicio_en=ainicio, fin_en=afin,
                    orden=aord, activo=True, requiere_ack=False,
                ))
                await session.flush()
        print("✅ 2 avisos creados")

        # ═══════════════════════════════════════════════════════════════
        # 18. SALARIOS BASE
        # ═══════════════════════════════════════════════════════════════
        for sid, srol, smonto in [
            (SALARIO_PROF_ID, "PROFESOR", 150000.00),
            (SALARIO_TUT_ID, "TUTOR", 80000.00),
            (SALARIO_NEXO_ID, "NEXO", 100000.00),
        ]:
            if not await id_exists(session, "salario_base", sid):
                session.add(SalarioBase(
                    id=sid, tenant_id=TENANT_ID, rol=srol,
                    monto=smonto, desde=date(TODAY.year, 1, 1),
                ))
                await session.flush()
        print("✅ 3 salarios base creados")

        # ── Commit ────────────────────────────────────────────────────
        await session.commit()

    # ── Summary ─────────────────────────────────────────────────────────
    print("""
╔══════════════════════════════════════════════════════════════════╗
║            🎉 MOCK DATA SEEDED SUCCESSFULLY!                   ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Usuarios de prueba (todos password: 123456):                  ║
║  ─────────────────────────────────────────────────────         ║
║  admin@activia-trace.com      ADMIN      Admin Trace           ║
║  profesor@activia-trace.com   PROFESOR   Carlos García         ║
║  tutor@activia-trace.com      TUTOR      María López           ║
║  alumno1@activia-trace.com    ALUMNO     Juan Pérez            ║
║  alumno2@activia-trace.com    ALUMNO     Ana Rodríguez         ║
║                                                                ║
║  Datos creados:                                                ║
║  - 2 carreras, 2 cohortes, 3 materias                         ║
║  - 4 asignaciones (profesor, tutor, 2 alumnos)                ║
║  - 2 slots semanales + 5 instancias de encuentro              ║
║  - 3 guardias (viernes)                                       ║
║  - 4 evaluaciones, 3 turnos disponibles                       ║
║  - 1 reserva activa, 1 resultado de TP (nota 8)               ║
║  - 2 tareas, 1 comentario                                     ║
║  - 2 avisos (global + por materia)                            ║
║  - 1 umbral de materia (60%)                                  ║
║  - 3 salarios base                                            ║
╚══════════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    asyncio.run(seed_mock())
