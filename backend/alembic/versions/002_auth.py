"""create usuario, sesion, recovery_token tables

Revision ID: 002
Revises: 001
Create Date: 2026-06-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "usuario",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_2fa_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("totp_secret", sa.String(512), nullable=True),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "email", name="uq_usuario_tenant_email"),
    )
    op.create_index(op.f("ix_usuario_tenant_id"), "usuario", ["tenant_id"])
    op.create_index(op.f("ix_usuario_email"), "usuario", ["email"])

    op.create_table(
        "sesion",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("refresh_token_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_revoked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["usuario.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sesion_user_id"), "sesion", ["user_id"])
    op.create_index(op.f("ix_sesion_refresh_token_hash"), "sesion", ["refresh_token_hash"])

    op.create_table(
        "recovery_token",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["usuario.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_recovery_token_user_id"), "recovery_token", ["user_id"])
    op.create_index(op.f("ix_recovery_token_token_hash"), "recovery_token", ["token_hash"])


def downgrade() -> None:
    op.drop_index(op.f("ix_recovery_token_token_hash"), table_name="recovery_token")
    op.drop_index(op.f("ix_recovery_token_user_id"), table_name="recovery_token")
    op.drop_table("recovery_token")

    op.drop_index(op.f("ix_sesion_refresh_token_hash"), table_name="sesion")
    op.drop_index(op.f("ix_sesion_user_id"), table_name="sesion")
    op.drop_table("sesion")

    op.drop_index(op.f("ix_usuario_email"), table_name="usuario")
    op.drop_index(op.f("ix_usuario_tenant_id"), table_name="usuario")
    op.drop_table("usuario")
