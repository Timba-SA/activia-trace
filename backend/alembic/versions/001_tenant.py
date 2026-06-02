"""create tenant table

Revision ID: 001
Revises:
Create Date: 2026-06-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "tenant",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tenant_slug"), "tenant", ["slug"], unique=True)
    op.create_index(op.f("ix_tenant_code"), "tenant", ["code"], unique=True)
    op.create_index(op.f("ix_tenant_is_active"), "tenant", ["is_active"])


def downgrade() -> None:
    op.drop_index(op.f("ix_tenant_is_active"), table_name="tenant")
    op.drop_index(op.f("ix_tenant_code"), table_name="tenant")
    op.drop_index(op.f("ix_tenant_slug"), table_name="tenant")
    op.drop_table("tenant")
