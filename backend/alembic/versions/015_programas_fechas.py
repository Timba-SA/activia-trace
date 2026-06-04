"""create programa_materia and fecha_academica tables, seed permissions

Revision ID: 015
Revises: 014
Create Date: 2026-06-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "015"
down_revision: str | None = "014"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE tipo_fecha_academica AS ENUM ('Parcial', 'TP', 'Coloquio', 'Recuperatorio')"
    )

    op.create_table(
        "programa_materia",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("materia_id", sa.Uuid(), nullable=False),
        sa.Column("carrera_id", sa.Uuid(), nullable=False),
        sa.Column("cohorte_id", sa.Uuid(), nullable=True),
        sa.Column("titulo", sa.String(255), nullable=False),
        sa.Column("referencia_archivo", sa.String(500), nullable=True),
        sa.Column("contenido_html", sa.Text(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("aprobado_en", sa.Date(), nullable=True),
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
        sa.ForeignKeyConstraint(["carrera_id"], ["carrera.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["cohorte_id"], ["cohorte.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "materia_id", "carrera_id", "cohorte_id", "version",
            name="uq_programa_version",
        ),
    )
    op.create_index(
        op.f("ix_programa_materia_tenant_id"), "programa_materia", ["tenant_id"]
    )
    op.create_index(
        "ix_programa_materia_tenant_activo", "programa_materia", ["tenant_id", "activo"]
    )
    op.create_index(
        op.f("ix_programa_materia_materia_id"), "programa_materia", ["materia_id"]
    )
    op.create_index(
        op.f("ix_programa_materia_carrera_id"), "programa_materia", ["carrera_id"]
    )
    op.create_index(
        op.f("ix_programa_materia_cohorte_id"), "programa_materia", ["cohorte_id"]
    )

    op.create_table(
        "fecha_academica",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("materia_id", sa.Uuid(), nullable=False),
        sa.Column("cohorte_id", sa.Uuid(), nullable=False),
        sa.Column(
            "tipo",
            sa.Enum(
                "Parcial",
                "TP",
                "Coloquio",
                "Recuperatorio",
                name="tipo_fecha_academica",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("numero", sa.Integer(), nullable=True),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("hora", sa.Time(), nullable=True),
        sa.Column("aula", sa.String(100), nullable=True),
        sa.Column("observaciones", sa.Text(), nullable=True),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_fecha_academica_tenant_id"), "fecha_academica", ["tenant_id"]
    )
    op.create_index(
        "ix_fecha_academica_tenant_materia", "fecha_academica", ["tenant_id", "materia_id"]
    )
    op.create_index(
        op.f("ix_fecha_academica_materia_id"), "fecha_academica", ["materia_id"]
    )
    op.create_index(
        op.f("ix_fecha_academica_cohorte_id"), "fecha_academica", ["cohorte_id"]
    )
    op.create_index(
        op.f("ix_fecha_academica_tipo"), "fecha_academica", ["tipo"]
    )

    _seed_permissions()


def _seed_permissions() -> None:
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions || :perm1::jsonb
               WHERE name IN ('COORDINADOR', 'ADMIN')
               AND NOT (permissions ? :perm1_str)"""
        ).bindparams(
            perm1=sa.text('\'["programas:gestionar"]\'::jsonb'),
            perm1_str="programas:gestionar",
        ),
    )

    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions || :perm2::jsonb
               WHERE name IN ('COORDINADOR', 'ADMIN')
               AND NOT (permissions ? :perm2_str)"""
        ).bindparams(
            perm2=sa.text('\'["programas:ver"]\'::jsonb'),
            perm2_str="programas:ver",
        ),
    )


def downgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions - :perm1_str
               WHERE permissions ? :perm1_str"""
        ).bindparams(perm1_str="programas:gestionar"),
    )
    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions - :perm2_str
               WHERE permissions ? :perm2_str"""
        ).bindparams(perm2_str="programas:ver"),
    )

    op.drop_table("fecha_academica")
    op.drop_table("programa_materia")

    op.execute("DROP TYPE IF EXISTS tipo_fecha_academica")
