"""create comunicacion table, add tenant config column, and comunicacion permissions

Revision ID: 008
Revises: 007
Create Date: 2026-06-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "008"
down_revision: str | None = "007"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # Create comunicacion table
    op.create_table(
        "comunicacion",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("enviado_por_id", sa.Uuid(), nullable=False),
        sa.Column("materia_id", sa.Uuid(), nullable=False),
        sa.Column("cohorte_id", sa.Uuid(), nullable=True),
        sa.Column("lote_id", sa.Uuid(), nullable=False),
        sa.Column("destinatario", sa.String(255), nullable=False),
        sa.Column("asunto", sa.String(255), nullable=False),
        sa.Column("cuerpo", sa.Text(), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default=sa.text("'Pendiente'")),
        sa.Column("requiere_aprobacion", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("error_msg", sa.Text(), nullable=True),
        sa.Column("enviado_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["enviado_por_id"], ["usuario.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["materia_id"], ["materia.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["cohorte_id"], ["cohorte.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_comunicacion_tenant_id"), "comunicacion", ["tenant_id"])
    op.create_index(op.f("ix_comunicacion_lote_id"), "comunicacion", ["lote_id"])
    op.create_index(op.f("ix_comunicacion_materia_id"), "comunicacion", ["materia_id"])
    op.create_index(op.f("ix_comunicacion_estado"), "comunicacion", ["estado"])
    op.create_index(
        op.f("ix_comunicacion_enviado_por_id"), "comunicacion", ["enviado_por_id"],
    )

    # Add tenant config column
    op.add_column(
        "tenant",
        sa.Column(
            "aprobacion_comunicaciones_requerida",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    # Add permissions to existing roles
    _add_comunicacion_permissions()


def _add_comunicacion_permissions() -> None:
    connection = op.get_bind()
    # Add comunicacion:enviar to PROFESOR, COORDINADOR, ADMIN
    for perm in ["comunicacion:enviar", "comunicacion:aprobar"]:
        connection.execute(
            sa.text(
                """UPDATE role
                   SET permissions = permissions || :perm::jsonb
                   WHERE name IN ('PROFESOR', 'COORDINADOR', 'ADMIN')
                   AND NOT (permissions ? :perm_str)"""
            ).bindparams(perm=sa.text(f"'[\"{perm}\"]'::jsonb"), perm_str=perm),
        )


def downgrade() -> None:
    op.drop_index(op.f("ix_comunicacion_enviado_por_id"), table_name="comunicacion")
    op.drop_index(op.f("ix_comunicacion_estado"), table_name="comunicacion")
    op.drop_index(op.f("ix_comunicacion_materia_id"), table_name="comunicacion")
    op.drop_index(op.f("ix_comunicacion_lote_id"), table_name="comunicacion")
    op.drop_index(op.f("ix_comunicacion_tenant_id"), table_name="comunicacion")
    op.drop_table("comunicacion")
    op.drop_column("tenant", "aprobacion_comunicaciones_requerida")
