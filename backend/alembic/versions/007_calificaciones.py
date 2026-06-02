"""create calificacion and umbral_materia tables, add calificaciones:configurar-umbral permission

Revision ID: 007
Revises: 006
Create Date: 2026-06-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "007"
down_revision: str | None = "006"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "calificacion",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("entrada_padron_id", sa.Uuid(), nullable=False),
        sa.Column("materia_id", sa.Uuid(), nullable=False),
        sa.Column("cohorte_id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=True),
        sa.Column("actividad_nombre", sa.String(255), nullable=False),
        sa.Column("calificacion", sa.String(50), nullable=False),
        sa.Column("es_numerica", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("aprobado", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("origen", sa.String(50), nullable=False, server_default=sa.text("'Importado'")),
        sa.Column("metadata_json", JSONB, nullable=True),
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
            ["entrada_padron_id"], ["entrada_padron.id"], ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["materia_id"], ["materia.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["cohorte_id"], ["cohorte.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuario.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_calificacion_tenant_id"), "calificacion", ["tenant_id"])
    op.create_index(op.f("ix_calificacion_materia_id"), "calificacion", ["materia_id"])
    op.create_index(op.f("ix_calificacion_cohorte_id"), "calificacion", ["cohorte_id"])
    op.create_index(
        op.f("ix_calificacion_entrada_padron_id"), "calificacion", ["entrada_padron_id"],
    )

    op.create_table(
        "umbral_materia",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("materia_id", sa.Uuid(), nullable=False),
        sa.Column("cohorte_id", sa.Uuid(), nullable=True),
        sa.Column("umbral_pct", sa.Float(), nullable=False, server_default=sa.text("60.0")),
        sa.Column(
            "valores_aprobados", JSONB, nullable=False,
            server_default=sa.text("'[\"Aprobado\", \"Promocionado\"]'"),
        ),
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
        sa.ForeignKeyConstraint(["cohorte_id"], ["cohorte.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_umbral_materia_tenant_id"), "umbral_materia", ["tenant_id"])
    op.create_index(op.f("ix_umbral_materia_materia_id"), "umbral_materia", ["materia_id"])

    _add_calificaciones_permission()


def _add_calificaciones_permission() -> None:
    connection = op.get_bind()
    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions || '["calificaciones:configurar-umbral"]'::jsonb
               WHERE name IN ('PROFESOR', 'COORDINADOR', 'ADMIN')
               AND NOT (permissions ? 'calificaciones:configurar-umbral')"""
        ),
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_umbral_materia_materia_id"), table_name="umbral_materia")
    op.drop_index(op.f("ix_umbral_materia_tenant_id"), table_name="umbral_materia")
    op.drop_table("umbral_materia")
    op.drop_index(
        op.f("ix_calificacion_entrada_padron_id"), table_name="calificacion",
    )
    op.drop_index(op.f("ix_calificacion_cohorte_id"), table_name="calificacion")
    op.drop_index(op.f("ix_calificacion_materia_id"), table_name="calificacion")
    op.drop_index(op.f("ix_calificacion_tenant_id"), table_name="calificacion")
    op.drop_table("calificacion")
