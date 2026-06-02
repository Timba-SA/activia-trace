"""create carrera cohorte materia tables

Revision ID: c5bf5701a1bf
Revises: 003
Create Date: 2026-06-02 15:36:50.990243

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c5bf5701a1bf"
down_revision: str | None = "003"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "carrera",
        sa.Column("codigo", sa.String(50), nullable=False),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("descripcion", sa.String(1000), nullable=True),
        sa.Column("duracion_anios", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "codigo", name="uk_carrera_codigo_tenant"),
    )
    op.create_index(op.f("ix_carrera_tenant_id"), "carrera", ["tenant_id"], unique=False)

    op.create_table(
        "cohorte",
        sa.Column("carrera_id", sa.Uuid(), nullable=False),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("anio", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["carrera_id"], ["carrera.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "carrera_id", "nombre", name="uk_cohorte_nombre_carrera_tenant"),
    )
    op.create_index(op.f("ix_cohorte_carrera_id"), "cohorte", ["carrera_id"], unique=False)
    op.create_index(op.f("ix_cohorte_tenant_id"), "cohorte", ["tenant_id"], unique=False)

    op.create_table(
        "materia",
        sa.Column("carrera_id", sa.Uuid(), nullable=True),
        sa.Column("codigo", sa.String(50), nullable=False),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("descripcion", sa.String(1000), nullable=True),
        sa.Column("carga_horaria", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["carrera_id"], ["carrera.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "codigo", name="uk_materia_codigo_tenant"),
    )
    op.create_index(op.f("ix_materia_carrera_id"), "materia", ["carrera_id"], unique=False)
    op.create_index(op.f("ix_materia_tenant_id"), "materia", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_materia_tenant_id"), table_name="materia")
    op.drop_index(op.f("ix_materia_carrera_id"), table_name="materia")
    op.drop_table("materia")
    op.drop_index(op.f("ix_cohorte_tenant_id"), table_name="cohorte")
    op.drop_index(op.f("ix_cohorte_carrera_id"), table_name="cohorte")
    op.drop_table("cohorte")
    op.drop_index(op.f("ix_carrera_tenant_id"), table_name="carrera")
    op.drop_table("carrera")
