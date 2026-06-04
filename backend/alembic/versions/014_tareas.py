"""create tarea and comentario_tarea tables, seed permissions

Revision ID: 014
Revises: 013
Create Date: 2026-06-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "014"
down_revision: str | None = "013"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE estado_tarea AS ENUM ('Pendiente', 'En progreso', 'Resuelta', 'Cancelada')"
    )

    op.create_table(
        "tarea",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column(
            "estado",
            sa.Enum(
                "Pendiente",
                "En progreso",
                "Resuelta",
                "Cancelada",
                name="estado_tarea",
                create_type=False,
            ),
            nullable=False,
            server_default=sa.text("'Pendiente'::estado_tarea"),
        ),
        sa.Column("asignado_a", sa.Uuid(), nullable=False),
        sa.Column("asignado_por", sa.Uuid(), nullable=False),
        sa.Column("materia_id", sa.Uuid(), nullable=True),
        sa.Column("contexto_id", sa.Uuid(), nullable=True),
        sa.Column("descripcion", sa.Text(), nullable=False),
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
            ["asignado_a"], ["usuario.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["asignado_por"], ["usuario.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["materia_id"], ["materia.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_tarea_tenant_id"), "tarea", ["tenant_id"]
    )
    op.create_index(
        "ix_tarea_tenant_asignado_a", "tarea", ["tenant_id", "asignado_a"]
    )
    op.create_index(
        "ix_tarea_tenant_estado", "tarea", ["tenant_id", "estado"]
    )

    op.create_table(
        "comentario_tarea",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("tarea_id", sa.Uuid(), nullable=False),
        sa.Column("autor_id", sa.Uuid(), nullable=False),
        sa.Column("texto", sa.Text(), nullable=False),
        sa.Column(
            "creado_at",
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
            ["tarea_id"], ["tarea.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["autor_id"], ["usuario.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_comentario_tarea_tenant_id"),
        "comentario_tarea",
        ["tenant_id"],
    )
    op.create_index(
        op.f("ix_comentario_tarea_tarea_id"),
        "comentario_tarea",
        ["tarea_id"],
    )
    op.create_index(
        op.f("ix_comentario_tarea_autor_id"),
        "comentario_tarea",
        ["autor_id"],
    )

    _seed_permissions()


def _seed_permissions() -> None:
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions || :perm::jsonb
               WHERE name IN ('PROFESOR', 'COORDINADOR', 'ADMIN')
               AND NOT (permissions ? :perm_str)"""
        ).bindparams(
            perm=sa.text('\'["tareas:gestionar"]\'::jsonb'),
            perm_str="tareas:gestionar",
        ),
    )


def downgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions - :perm_str
               WHERE permissions ? :perm_str"""
        ).bindparams(perm_str="tareas:gestionar"),
    )

    op.drop_table("comentario_tarea")
    op.drop_table("tarea")

    op.execute("DROP TYPE IF EXISTS estado_tarea")
