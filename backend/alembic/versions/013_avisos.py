"""create avisos and acknowledgment tables, seed permissions

Revision ID: 013
Revises: 012
Create Date: 2026-06-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "013"
down_revision: str | None = "012"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # Create enum types
    op.execute(
        "CREATE TYPE alcance_aviso AS ENUM ('Global', 'PorMateria', 'PorCohorte', 'PorRol')"
    )
    op.execute(
        "CREATE TYPE severidad_aviso AS ENUM ('Info', 'Advertencia', 'Critico')"
    )

    # Create aviso table
    op.create_table(
        "aviso",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column(
            "alcance",
            sa.Enum(
                "Global",
                "PorMateria",
                "PorCohorte",
                "PorRol",
                name="alcance_aviso",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("materia_id", sa.Uuid(), nullable=True),
        sa.Column("cohorte_id", sa.Uuid(), nullable=True),
        sa.Column("rol_destino", sa.String(100), nullable=True),
        sa.Column(
            "severidad",
            sa.Enum(
                "Info",
                "Advertencia",
                "Critico",
                name="severidad_aviso",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("titulo", sa.String(255), nullable=False),
        sa.Column("cuerpo", sa.Text(), nullable=False),
        sa.Column(
            "inicio_en", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column(
            "fin_en", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column("orden", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "activo", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column(
            "requiere_ack",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
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
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["tenant.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["materia_id"], ["materia.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["cohorte_id"], ["cohorte.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_aviso_tenant_id"), "aviso", ["tenant_id"]
    )
    op.create_index(
        op.f("ix_aviso_materia_id"), "aviso", ["materia_id"]
    )
    op.create_index(
        op.f("ix_aviso_cohorte_id"), "aviso", ["cohorte_id"]
    )
    op.create_index(
        "ix_aviso_tenant_activo", "aviso", ["tenant_id", "activo"]
    )
    op.create_index(
        "ix_aviso_tenant_alcance", "aviso", ["tenant_id", "alcance"]
    )

    # Create acknowledgment_aviso table
    op.create_table(
        "acknowledgment_aviso",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("aviso_id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column(
            "confirmado_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
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
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["tenant.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["aviso_id"], ["aviso.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["usuario_id"], ["usuario.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "aviso_id", "usuario_id", name="uq_ack_aviso_usuario"
        ),
    )
    op.create_index(
        op.f("ix_acknowledgment_aviso_tenant_id"),
        "acknowledgment_aviso",
        ["tenant_id"],
    )
    op.create_index(
        op.f("ix_acknowledgment_aviso_aviso_id"),
        "acknowledgment_aviso",
        ["aviso_id"],
    )
    op.create_index(
        op.f("ix_acknowledgment_aviso_usuario_id"),
        "acknowledgment_aviso",
        ["usuario_id"],
    )

    # Seed permissions
    _seed_permissions()


def _seed_permissions() -> None:
    connection = op.get_bind()

    # avisos:publicar -> COORDINADOR, ADMIN
    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions || :perm::jsonb
               WHERE name IN ('COORDINADOR', 'ADMIN')
               AND NOT (permissions ? :perm_str)"""
        ).bindparams(
            perm=sa.text('\'["avisos:publicar"]\'::jsonb'),
            perm_str="avisos:publicar",
        ),
    )


def downgrade() -> None:
    connection = op.get_bind()

    # Remove permissions
    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions - :perm_str
               WHERE permissions ? :perm_str"""
        ).bindparams(perm_str="avisos:publicar"),
    )

    # Drop tables
    op.drop_table("acknowledgment_aviso")
    op.drop_table("aviso")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS severidad_aviso")
    op.execute("DROP TYPE IF EXISTS alcance_aviso")
