"""create encuentros and guardias tables + seed permissions

Revision ID: 011
Revises: 010
Create Date: 2026-06-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "011"
down_revision: str | None = "010"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE dia_semana AS ENUM ('Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo')")
    op.execute("CREATE TYPE estado_instancia AS ENUM ('Programado', 'Realizado', 'Cancelado')")
    op.execute("CREATE TYPE dia_semana_guardia AS ENUM ('Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo')")
    op.execute("CREATE TYPE estado_guardia AS ENUM ('Pendiente', 'Realizada', 'Cancelada')")

    # Create slot_encuentro table
    op.create_table(
        "slot_encuentro",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("asignacion_id", sa.Uuid(), nullable=False),
        sa.Column("materia_id", sa.Uuid(), nullable=False),
        sa.Column("titulo", sa.String(255), nullable=False),
        sa.Column("hora", sa.Time(), nullable=False),
        sa.Column("dia_semana", sa.Enum("Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo", name="dia_semana", create_type=False), nullable=False),
        sa.Column("fecha_inicio", sa.Date(), nullable=False),
        sa.Column("cant_semanas", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("fecha_unica", sa.Date(), nullable=True),
        sa.Column("meet_url", sa.String(500), nullable=True),
        sa.Column("vig_desde", sa.Date(), nullable=False),
        sa.Column("vig_hasta", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["asignacion_id"], ["asignacion.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["materia_id"], ["materia.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_slot_encuentro_asignacion_id"), "slot_encuentro", ["asignacion_id"])
    op.create_index(op.f("ix_slot_encuentro_materia_id"), "slot_encuentro", ["materia_id"])
    op.create_index(op.f("ix_slot_encuentro_tenant_id"), "slot_encuentro", ["tenant_id"])

    # Create instancia_encuentro table
    op.create_table(
        "instancia_encuentro",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("slot_id", sa.Uuid(), nullable=True),
        sa.Column("materia_id", sa.Uuid(), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("hora", sa.Time(), nullable=False),
        sa.Column("titulo", sa.String(255), nullable=False),
        sa.Column("estado", sa.Enum("Programado", "Realizado", "Cancelado", name="estado_instancia", create_type=False), nullable=False, server_default=sa.text("'Programado'")),
        sa.Column("meet_url", sa.String(500), nullable=True),
        sa.Column("video_url", sa.String(500), nullable=True),
        sa.Column("comentario", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["slot_id"], ["slot_encuentro.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["materia_id"], ["materia.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_instancia_encuentro_slot_id"), "instancia_encuentro", ["slot_id"])
    op.create_index(op.f("ix_instancia_encuentro_materia_id"), "instancia_encuentro", ["materia_id"])
    op.create_index(op.f("ix_instancia_encuentro_tenant_id"), "instancia_encuentro", ["tenant_id"])

    # Create guardia table
    op.create_table(
        "guardia",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("asignacion_id", sa.Uuid(), nullable=False),
        sa.Column("materia_id", sa.Uuid(), nullable=False),
        sa.Column("carrera_id", sa.Uuid(), nullable=False),
        sa.Column("cohorte_id", sa.Uuid(), nullable=False),
        sa.Column("dia", sa.Enum("Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo", name="dia_semana_guardia", create_type=False), nullable=False),
        sa.Column("horario", sa.String(50), nullable=False),
        sa.Column("estado", sa.Enum("Pendiente", "Realizada", "Cancelada", name="estado_guardia", create_type=False), nullable=False, server_default=sa.text("'Pendiente'")),
        sa.Column("comentarios", sa.String(1000), nullable=True),
        sa.Column("creada_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["asignacion_id"], ["asignacion.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["materia_id"], ["materia.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["carrera_id"], ["carrera.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["cohorte_id"], ["cohorte.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_guardia_asignacion_id"), "guardia", ["asignacion_id"])
    op.create_index(op.f("ix_guardia_materia_id"), "guardia", ["materia_id"])
    op.create_index(op.f("ix_guardia_carrera_id"), "guardia", ["carrera_id"])
    op.create_index(op.f("ix_guardia_cohorte_id"), "guardia", ["cohorte_id"])
    op.create_index(op.f("ix_guardia_tenant_id"), "guardia", ["tenant_id"])

    # Seed permissions
    _seed_permissions()


def _seed_permissions() -> None:
    connection = op.get_bind()

    # encuentros:gestionar -> PROFESOR, COORDINADOR
    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions || :perm::jsonb
               WHERE name IN ('PROFESOR', 'COORDINADOR')
               AND NOT (permissions ? :perm_str)"""
        ).bindparams(perm=sa.text('\'["encuentros:gestionar"]\'::jsonb'), perm_str="encuentros:gestionar"),
    )

    # encuentros:ver -> COORDINADOR, ADMIN
    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions || :perm::jsonb
               WHERE name IN ('COORDINADOR', 'ADMIN')
               AND NOT (permissions ? :perm_str)"""
        ).bindparams(perm=sa.text('\'["encuentros:ver"]\'::jsonb'), perm_str="encuentros:ver"),
    )

    # guardias:registrar -> TUTOR
    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions || :perm::jsonb
               WHERE name = 'TUTOR'
               AND NOT (permissions ? :perm_str)"""
        ).bindparams(perm=sa.text('\'["guardias:registrar"]\'::jsonb'), perm_str="guardias:registrar"),
    )

    # guardias:ver -> COORDINADOR, ADMIN
    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions || :perm::jsonb
               WHERE name IN ('COORDINADOR', 'ADMIN')
               AND NOT (permissions ? :perm_str)"""
        ).bindparams(perm=sa.text('\'["guardias:ver"]\'::jsonb'), perm_str="guardias:ver"),
    )


def downgrade() -> None:
    # Remove permissions (reverse order)
    connection = op.get_bind()
    for perm in ["guardias:ver", "guardias:registrar", "encuentros:ver", "encuentros:gestionar"]:
        connection.execute(
            sa.text(
                """UPDATE role
                   SET permissions = permissions - :perm_str
                   WHERE permissions ? :perm_str"""
            ).bindparams(perm_str=perm),
        )

    # Drop tables
    op.drop_table("guardia")
    op.drop_table("instancia_encuentro")
    op.drop_table("slot_encuentro")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS estado_guardia")
    op.execute("DROP TYPE IF EXISTS dia_semana_guardia")
    op.execute("DROP TYPE IF EXISTS estado_instancia")
    op.execute("DROP TYPE IF EXISTS dia_semana")
