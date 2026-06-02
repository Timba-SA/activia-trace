"""add columns to usuario, create asignacion table, add new permissions

Revision ID: 005
Revises: c5bf5701a1bf
Create Date: 2026-06-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "005"
down_revision: str | None = "c5bf5701a1bf"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("usuario", sa.Column("nombre", sa.String(255), nullable=True))
    op.add_column("usuario", sa.Column("apellido", sa.String(255), nullable=True))
    op.add_column("usuario", sa.Column("dni", sa.Text(), nullable=True))
    op.add_column("usuario", sa.Column("cuil", sa.Text(), nullable=True))
    op.add_column("usuario", sa.Column("telefono", sa.String(50), nullable=True))
    op.add_column("usuario", sa.Column("direccion", sa.String(500), nullable=True))
    op.add_column("usuario", sa.Column("fecha_nacimiento", sa.Date(), nullable=True))
    op.add_column("usuario", sa.Column("legajo", sa.String(50), nullable=True))
    op.add_column("usuario", sa.Column("cbu", sa.Text(), nullable=True))
    op.create_unique_constraint("uq_usuario_legajo_tenant", "usuario", ["tenant_id", "legajo"])
    op.create_index(
        op.f("uix_usuario_tenant_legajo"),
        "usuario",
        ["tenant_id", "legajo"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "asignacion",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("rol", sa.String(50), nullable=False),
        sa.Column("carrera_id", sa.Uuid(), nullable=True),
        sa.Column("materia_id", sa.Uuid(), nullable=True),
        sa.Column("cohorte_id", sa.Uuid(), nullable=True),
        sa.Column("responsable_id", sa.Uuid(), nullable=True),
        sa.Column("fecha_inicio", sa.Date(), nullable=False),
        sa.Column("fecha_fin", sa.Date(), nullable=True),
        sa.Column("comisiones", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuario.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["carrera_id"], ["carrera.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["materia_id"], ["materia.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["cohorte_id"], ["cohorte.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["responsable_id"], ["usuario.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_asignacion_tenant_id"), "asignacion", ["tenant_id"])
    op.create_index(op.f("ix_asignacion_usuario_id"), "asignacion", ["usuario_id"])
    op.create_index(op.f("ix_asignacion_carrera_id"), "asignacion", ["carrera_id"])
    op.create_index(op.f("ix_asignacion_materia_id"), "asignacion", ["materia_id"])
    op.create_index(op.f("ix_asignacion_cohorte_id"), "asignacion", ["cohorte_id"])
    op.create_index(op.f("ix_asignacion_responsable_id"), "asignacion", ["responsable_id"])

    _add_new_permissions()


def _add_new_permissions() -> None:
    connection = op.get_bind()
    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions || '["usuarios:asignar", "usuarios:ver-pii"]'::jsonb
               WHERE name IN ('ADMIN', 'COORDINADOR')
               AND NOT (permissions ? 'usuarios:asignar')"""
        ),
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_asignacion_responsable_id"), table_name="asignacion")
    op.drop_index(op.f("ix_asignacion_cohorte_id"), table_name="asignacion")
    op.drop_index(op.f("ix_asignacion_materia_id"), table_name="asignacion")
    op.drop_index(op.f("ix_asignacion_carrera_id"), table_name="asignacion")
    op.drop_index(op.f("ix_asignacion_usuario_id"), table_name="asignacion")
    op.drop_index(op.f("ix_asignacion_tenant_id"), table_name="asignacion")
    op.drop_table("asignacion")
    op.drop_index(
        op.f("uix_usuario_tenant_legajo"),
        table_name="usuario",
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.drop_constraint("uq_usuario_legajo_tenant", "usuario", type_="unique")
    op.drop_column("usuario", "cbu")
    op.drop_column("usuario", "legajo")
    op.drop_column("usuario", "fecha_nacimiento")
    op.drop_column("usuario", "direccion")
    op.drop_column("usuario", "telefono")
    op.drop_column("usuario", "cuil")
    op.drop_column("usuario", "dni")
    op.drop_column("usuario", "apellido")
    op.drop_column("usuario", "nombre")
