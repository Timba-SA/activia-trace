"""create evaluaciones and coloquios tables, seed permissions

Revision ID: 012
Revises: 011
Create Date: 2026-06-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "012"
down_revision: str | None = "011"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE tipo_evaluacion AS ENUM ('Parcial', 'TP', 'Coloquio', 'Recuperatorio')")
    op.execute("CREATE TYPE estado_reserva AS ENUM ('Activa', 'Cancelada')")

    # Create evaluacion table
    op.create_table(
        "evaluacion",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("materia_id", sa.Uuid(), nullable=False),
        sa.Column("cohorte_id", sa.Uuid(), nullable=False),
        sa.Column("tipo", sa.Enum("Parcial", "TP", "Coloquio", "Recuperatorio", name="tipo_evaluacion", create_type=False), nullable=False),
        sa.Column("instancia", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["materia_id"], ["materia.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["cohorte_id"], ["cohorte.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_evaluacion_tenant_id"), "evaluacion", ["tenant_id"])
    op.create_index(op.f("ix_evaluacion_materia_id"), "evaluacion", ["materia_id"])
    op.create_index(op.f("ix_evaluacion_cohorte_id"), "evaluacion", ["cohorte_id"])

    # Create turno_disponible table
    op.create_table(
        "turno_disponible",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("evaluacion_id", sa.Uuid(), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("hora", sa.Time(), nullable=False),
        sa.Column("cupo_total", sa.Integer(), nullable=False),
        sa.Column("cupos_restantes", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["evaluacion_id"], ["evaluacion.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("evaluacion_id", "fecha", "hora", name="uk_turno_evaluacion_fecha_hora"),
    )
    op.create_index(op.f("ix_turno_disponible_tenant_id"), "turno_disponible", ["tenant_id"])
    op.create_index(op.f("ix_turno_disponible_evaluacion_id"), "turno_disponible", ["evaluacion_id"])

    # Create reserva_evaluacion table
    op.create_table(
        "reserva_evaluacion",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("evaluacion_id", sa.Uuid(), nullable=False),
        sa.Column("alumno_id", sa.Uuid(), nullable=False),
        sa.Column("turno_id", sa.Uuid(), nullable=False),
        sa.Column("fecha_hora", sa.DateTime(timezone=True), nullable=False),
        sa.Column("estado", sa.Enum("Activa", "Cancelada", name="estado_reserva", create_type=False), nullable=False, server_default=sa.text("'Activa'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["evaluacion_id"], ["evaluacion.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["alumno_id"], ["usuario.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["turno_id"], ["turno_disponible.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reserva_evaluacion_tenant_id"), "reserva_evaluacion", ["tenant_id"])
    op.create_index(op.f("ix_reserva_evaluacion_evaluacion_id"), "reserva_evaluacion", ["evaluacion_id"])
    op.create_index(op.f("ix_reserva_evaluacion_alumno_id"), "reserva_evaluacion", ["alumno_id"])
    op.create_index(op.f("ix_reserva_evaluacion_turno_id"), "reserva_evaluacion", ["turno_id"])

    # Create resultado_evaluacion table
    op.create_table(
        "resultado_evaluacion",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("evaluacion_id", sa.Uuid(), nullable=False),
        sa.Column("alumno_id", sa.Uuid(), nullable=False),
        sa.Column("nota_final", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["evaluacion_id"], ["evaluacion.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["alumno_id"], ["usuario.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_resultado_evaluacion_tenant_id"), "resultado_evaluacion", ["tenant_id"])
    op.create_index(op.f("ix_resultado_evaluacion_evaluacion_id"), "resultado_evaluacion", ["evaluacion_id"])
    op.create_index(op.f("ix_resultado_evaluacion_alumno_id"), "resultado_evaluacion", ["alumno_id"])

    # Create convocatoria_alumno table
    op.create_table(
        "convocatoria_alumno",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("evaluacion_id", sa.Uuid(), nullable=False),
        sa.Column("alumno_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["evaluacion_id"], ["evaluacion.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["alumno_id"], ["usuario.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("evaluacion_id", "alumno_id", name="uk_convocatoria_evaluacion_alumno"),
    )
    op.create_index(op.f("ix_convocatoria_alumno_tenant_id"), "convocatoria_alumno", ["tenant_id"])
    op.create_index(op.f("ix_convocatoria_alumno_evaluacion_id"), "convocatoria_alumno", ["evaluacion_id"])
    op.create_index(op.f("ix_convocatoria_alumno_alumno_id"), "convocatoria_alumno", ["alumno_id"])

    # Seed permissions
    _seed_permissions()


def _seed_permissions() -> None:
    connection = op.get_bind()

    # coloquios:gestionar -> COORDINADOR, ADMIN
    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions || :perm::jsonb
               WHERE name IN ('COORDINADOR', 'ADMIN')
               AND NOT (permissions ? :perm_str)"""
        ).bindparams(perm=sa.text('\'["coloquios:gestionar"]\'::jsonb'), perm_str="coloquios:gestionar"),
    )

    # coloquios:ver -> COORDINADOR, ADMIN
    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions || :perm::jsonb
               WHERE name IN ('COORDINADOR', 'ADMIN')
               AND NOT (permissions ? :perm_str)"""
        ).bindparams(perm=sa.text('\'["coloquios:ver"]\'::jsonb'), perm_str="coloquios:ver"),
    )

    # coloquios:reservar -> ALUMNO
    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions || :perm::jsonb
               WHERE name = 'ALUMNO'
               AND NOT (permissions ? :perm_str)"""
        ).bindparams(perm=sa.text('\'["coloquios:reservar"]\'::jsonb'), perm_str="coloquios:reservar"),
    )


def downgrade() -> None:
    connection = op.get_bind()

    # Remove permissions
    for perm in ["coloquios:gestionar", "coloquios:ver", "coloquios:reservar"]:
        connection.execute(
            sa.text(
                """UPDATE role
                   SET permissions = permissions - :perm_str
                   WHERE permissions ? :perm_str"""
            ).bindparams(perm_str=perm),
        )

    # Drop tables
    op.drop_table("convocatoria_alumno")
    op.drop_table("resultado_evaluacion")
    op.drop_table("reserva_evaluacion")
    op.drop_table("turno_disponible")
    op.drop_table("evaluacion")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS estado_reserva")
    op.execute("DROP TYPE IF EXISTS tipo_evaluacion")
