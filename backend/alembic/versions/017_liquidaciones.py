"""create liquidaciones, facturas and grilla tables

Revision ID: 017
Revises: 016
Create Date: 2026-06-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "017"
down_revision: str | None = "016"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "salario_base",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("rol", sa.String(20), nullable=False),
        sa.Column("monto", sa.Numeric(12, 2), nullable=False),
        sa.Column("desde", sa.Date(), nullable=False),
        sa.Column("hasta", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"], name=op.f("fk_salario_base_tenant_id")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_salario_base")),
    )
    op.create_index(
        "uq_salario_base_vigente", "salario_base",
        ["tenant_id", "rol", "desde"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "salario_plus",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("grupo", sa.String(50), nullable=False),
        sa.Column("rol", sa.String(20), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("monto", sa.Numeric(12, 2), nullable=False),
        sa.Column("tope_acumulacion", sa.Integer(), nullable=True),
        sa.Column("desde", sa.Date(), nullable=False),
        sa.Column("hasta", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"], name=op.f("fk_salario_plus_tenant_id")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_salario_plus")),
    )

    op.create_table(
        "materia_grupo_plus",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("materia_id", sa.Uuid(), nullable=False),
        sa.Column("grupo", sa.String(50), nullable=False),
        sa.Column("desde", sa.Date(), nullable=False),
        sa.Column("hasta", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"], name=op.f("fk_materia_grupo_plus_tenant_id")),
        sa.ForeignKeyConstraint(["materia_id"], ["materia.id"], name=op.f("fk_materia_grupo_plus_materia_id")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_materia_grupo_plus")),
    )
    op.create_index(
        "uq_materia_grupo_vigente", "materia_grupo_plus",
        ["tenant_id", "materia_id", "grupo", "desde"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "liquidacion",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("cohorte_id", sa.Uuid(), nullable=False),
        sa.Column("periodo", sa.String(7), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("rol", sa.String(20), nullable=False),
        sa.Column("comisiones", sa.JSON(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("monto_base", sa.Numeric(12, 2), nullable=False),
        sa.Column("monto_plus", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("total", sa.Numeric(12, 2), nullable=False),
        sa.Column("es_nexo", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("excluido_por_factura", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("estado", sa.String(10), nullable=False, server_default=sa.text("'Abierta'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"], name=op.f("fk_liquidacion_tenant_id")),
        sa.ForeignKeyConstraint(["cohorte_id"], ["cohorte.id"], name=op.f("fk_liquidacion_cohorte_id")),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuario.id"], name=op.f("fk_liquidacion_usuario_id")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_liquidacion")),
    )
    op.create_index(
        "uq_liquidacion_periodo", "liquidacion",
        ["tenant_id", "cohorte_id", "periodo", "usuario_id"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "factura",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("periodo", sa.String(7), nullable=False),
        sa.Column("detalle", sa.Text(), nullable=True),
        sa.Column("referencia_archivo", sa.Text(), nullable=False),
        sa.Column("tamano_kb", sa.Numeric(10, 2), nullable=True),
        sa.Column("estado", sa.String(10), nullable=False, server_default=sa.text("'Pendiente'")),
        sa.Column("cargada_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("abonada_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"], name=op.f("fk_factura_tenant_id")),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuario.id"], name=op.f("fk_factura_usuario_id")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_factura")),
    )

    # Add usuario.facturador column
    op.add_column(
        "usuario",
        sa.Column("facturador", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )

    # Seed permissions: add liquidaciones:* to FINANZAS role
    conn = op.get_bind()
    if conn.engine.name == "postgresql":
        liquidaciones_perms = [
            "liquidaciones:calcular",
            "liquidaciones:ver",
            "liquidaciones:cerrar",
            "liquidaciones:exportar",
            "liquidaciones:configurar-salarios",
            "liquidaciones:gestionar-facturas",
        ]
        for perm in liquidaciones_perms:
            conn.execute(
                sa.text(
                    "UPDATE \"role\" SET permissions = permissions || CAST(:perm AS jsonb) "
                    "WHERE name = 'FINANZAS' AND deleted_at IS NULL"
                ),
                {"perm": f'"{perm}"'},
            )
        conn.execute(
            sa.text(
                "UPDATE \"role\" SET permissions = permissions || '\"liquidaciones:ver\"'::jsonb "
                "WHERE name = 'ADMIN' AND deleted_at IS NULL"
            ),
        )


def downgrade() -> None:
    op.drop_table("factura")
    op.drop_table("liquidacion")
    op.drop_table("materia_grupo_plus")
    op.drop_table("salario_plus")
    op.drop_table("salario_base")
    op.drop_column("usuario", "facturador")
