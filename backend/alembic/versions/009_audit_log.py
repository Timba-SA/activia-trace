"""create audit_log table with append-only trigger and audit/impersonation permissions

Revision ID: 009
Revises: 008
Create Date: 2026-06-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "009"
down_revision: str | None = "008"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # Create audit_log table
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=False),
        sa.Column("impersonado_id", sa.Uuid(), nullable=True),
        sa.Column("materia_id", sa.Uuid(), nullable=True),
        sa.Column("fecha_hora", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("accion", sa.String(100), nullable=False),
        sa.Column("detalle", sa.JSON(), nullable=True),
        sa.Column("filas_afectadas", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("ip", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["actor_id"], ["usuario.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["impersonado_id"], ["usuario.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["materia_id"], ["materia.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_log_tenant_fecha"), "audit_log", ["tenant_id", "fecha_hora"])
    op.create_index(op.f("ix_audit_log_actor_id"), "audit_log", ["actor_id"])
    op.create_index(op.f("ix_audit_log_accion"), "audit_log", ["accion"])

    # Append-only trigger: reject UPDATE and DELETE on audit_log
    op.execute(
        """
        CREATE OR REPLACE FUNCTION reject_audit_log_modification()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'audit_log is append-only: UPDATE and DELETE are not permitted';
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_audit_log_append_only
        BEFORE UPDATE OR DELETE ON audit_log
        FOR EACH ROW
        EXECUTE FUNCTION reject_audit_log_modification();
        """
    )

    # Add permissions to existing roles
    _add_audit_permissions()


def _add_audit_permissions() -> None:
    connection = op.get_bind()

    # auditoria:ver to COORDINADOR, ADMIN, FINANZAS
    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions || :perm::jsonb
               WHERE name IN ('COORDINADOR', 'ADMIN', 'FINANZAS')
               AND NOT (permissions ? :perm_str)"""
        ).bindparams(perm=sa.text('\'["auditoria:ver"]\'::jsonb'), perm_str="auditoria:ver"),
    )

    # impersonacion:usar to ADMIN only
    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions || :perm::jsonb
               WHERE name = 'ADMIN'
               AND NOT (permissions ? :perm_str)"""
        ).bindparams(perm=sa.text('\'["impersonacion:usar"]\'::jsonb'), perm_str="impersonacion:usar"),
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_audit_log_append_only ON audit_log")
    op.execute("DROP FUNCTION IF EXISTS reject_audit_log_modification()")
    op.drop_index(op.f("ix_audit_log_tenant_fecha"), table_name="audit_log")
    op.drop_index(op.f("ix_audit_log_actor_id"), table_name="audit_log")
    op.drop_index(op.f("ix_audit_log_accion"), table_name="audit_log")
    op.drop_table("audit_log")
