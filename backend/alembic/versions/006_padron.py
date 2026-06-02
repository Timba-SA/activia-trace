"""create version_padron and entrada_padron tables, add padron:cargar permission

Revision ID: 006
Revises: 005
Create Date: 2026-06-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "006"
down_revision: str | None = "005"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "version_padron",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("materia_id", sa.Uuid(), nullable=False),
        sa.Column("cohorte_id", sa.Uuid(), nullable=False),
        sa.Column("activa", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("creada_por", sa.Uuid(), nullable=False),
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
        sa.ForeignKeyConstraint(["materia_id"], ["materia.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["cohorte_id"], ["cohorte.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["creada_por"], ["usuario.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_version_padron_tenant_id"), "version_padron", ["tenant_id"])
    op.create_index(op.f("ix_version_padron_materia_id"), "version_padron", ["materia_id"])
    op.create_index(op.f("ix_version_padron_cohorte_id"), "version_padron", ["cohorte_id"])

    op.create_table(
        "entrada_padron",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("version_padron_id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=True),
        sa.Column("legajo", sa.String(50), nullable=False),
        sa.Column("nombre_completo", sa.String(500), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("estado", sa.String(50), nullable=False, server_default=sa.text("'activo'")),
        sa.Column("datos_extra", JSONB, nullable=True),
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
        sa.ForeignKeyConstraint(
            ["version_padron_id"], ["version_padron.id"], ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuario.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_entrada_padron_tenant_id"), "entrada_padron", ["tenant_id"])
    op.create_index(
        op.f("ix_entrada_padron_version_padron_id"),
        "entrada_padron",
        ["version_padron_id"],
    )
    op.create_index(op.f("ix_entrada_padron_usuario_id"), "entrada_padron", ["usuario_id"])

    _add_padron_permission()


def _add_padron_permission() -> None:
    connection = op.get_bind()
    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions || '["padron:cargar"]'::jsonb
               WHERE name IN ('ADMIN', 'COORDINADOR')
               AND NOT (permissions ? 'padron:cargar')"""
        ),
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_entrada_padron_usuario_id"), table_name="entrada_padron")
    op.drop_index(
        op.f("ix_entrada_padron_version_padron_id"),
        table_name="entrada_padron",
    )
    op.drop_index(op.f("ix_entrada_padron_tenant_id"), table_name="entrada_padron")
    op.drop_table("entrada_padron")
    op.drop_index(op.f("ix_version_padron_cohorte_id"), table_name="version_padron")
    op.drop_index(op.f("ix_version_padron_materia_id"), table_name="version_padron")
    op.drop_index(op.f("ix_version_padron_tenant_id"), table_name="version_padron")
    op.drop_table("version_padron")
