"""create mensaje table

Revision ID: 016
Revises: 015
Create Date: 2026-06-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "016"
down_revision: str | None = "015"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "mensaje",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("remitente_id", sa.Uuid(), nullable=False),
        sa.Column("destinatario_id", sa.Uuid(), nullable=False),
        sa.Column("hilo_id", sa.Uuid(), nullable=True),
        sa.Column("asunto", sa.String(255), nullable=False),
        sa.Column("cuerpo", sa.Text(), nullable=False),
        sa.Column("leido", sa.Boolean(), nullable=False, server_default=sa.text("false")),
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
        sa.ForeignKeyConstraint(["remitente_id"], ["usuario.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["destinatario_id"], ["usuario.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_mensaje_tenant_id"), "mensaje", ["tenant_id"]
    )
    op.create_index(
        "ix_mensaje_tenant_destinatario", "mensaje", ["tenant_id", "destinatario_id"]
    )
    op.create_index(
        "ix_mensaje_tenant_hilo", "mensaje", ["tenant_id", "hilo_id"]
    )
    op.create_index(
        op.f("ix_mensaje_remitente_id"), "mensaje", ["remitente_id"]
    )
    op.create_index(
        op.f("ix_mensaje_destinatario_id"), "mensaje", ["destinatario_id"]
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_mensaje_destinatario_id"), table_name="mensaje")
    op.drop_index(op.f("ix_mensaje_remitente_id"), table_name="mensaje")
    op.drop_index("ix_mensaje_tenant_hilo", table_name="mensaje")
    op.drop_index("ix_mensaje_tenant_destinatario", table_name="mensaje")
    op.drop_index(op.f("ix_mensaje_tenant_id"), table_name="mensaje")
    op.drop_table("mensaje")
