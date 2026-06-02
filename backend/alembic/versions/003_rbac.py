"""create role and usuario_role tables with seed data

Revision ID: 003
Revises: 002
Create Date: 2026-06-02
"""

import json
import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "003"
down_revision: str | None = "002"
branch_labels: str | None = None
depends_on: str | None = None


SYSTEM_ROLES = {
    "ALUMNO": {
        "description": "Estudiante que cursa materias",
        "permissions": [
            "academico:ver_estado_propio",
            "evaluaciones:reservar",
            "comunicacion:confirmar_avisos",
        ],
    },
    "TUTOR": {
        "description": "Auxiliar / ayudante de cátedra",
        "permissions": [
            "comunicacion:confirmar_avisos",
            "atrasados:ver",
            "entregas:detectar_sin_corregir",
            "encuentros:gestionar",
            "guardias:registrar",
        ],
    },
    "PROFESOR": {
        "description": "Docente a cargo de una o más comisiones",
        "permissions": [
            "comunicacion:confirmar_avisos",
            "calificaciones:importar",
            "atrasados:ver",
            "entregas:detectar_sin_corregir",
            "comunicacion:enviar",
            "encuentros:gestionar",
            "guardias:registrar",
            "tareas:gestionar",
        ],
    },
    "COORDINADOR": {
        "description": "Responsable de un conjunto de materias o de una cohorte",
        "permissions": [
            "comunicacion:confirmar_avisos",
            "calificaciones:importar",
            "atrasados:ver",
            "entregas:detectar_sin_corregir",
            "comunicacion:enviar",
            "comunicacion:aprobar_masivas",
            "encuentros:gestionar",
            "guardias:registrar",
            "tareas:gestionar",
            "avisos:publicar",
            "equipos:gestionar",
            "auditoria:ver",
        ],
    },
    "NEXO": {
        "description": "Rol de articulación / enlace transversal",
        "permissions": [
            "comunicacion:confirmar_avisos",
            "atrasados:ver",
            "entregas:detectar_sin_corregir",
            "comunicacion:enviar",
            "encuentros:gestionar",
            "avisos:publicar",
            "auditoria:ver",
        ],
    },
    "ADMIN": {
        "description": "Administrador del sistema dentro del tenant",
        "permissions": [
            "comunicacion:confirmar_avisos",
            "calificaciones:importar",
            "atrasados:ver",
            "entregas:detectar_sin_corregir",
            "comunicacion:enviar",
            "comunicacion:aprobar_masivas",
            "encuentros:gestionar",
            "guardias:registrar",
            "tareas:gestionar",
            "avisos:publicar",
            "equipos:gestionar",
            "estructura:gestionar",
            "usuarios:gestionar",
            "auditoria:ver",
            "tenant:configurar",
            "roles:gestionar",
        ],
    },
    "FINANZAS": {
        "description": "Responsable de liquidaciones y honorarios",
        "permissions": [
            "comunicacion:confirmar_avisos",
            "auditoria:ver",
            "liquidaciones:grilla_salarial",
            "liquidaciones:calcular_cerrar",
            "liquidaciones:facturas",
        ],
    },
}


def upgrade() -> None:
    op.create_table(
        "role",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("permissions", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("is_system_role", sa.Boolean(), nullable=False, server_default=sa.text("false")),
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
        sa.UniqueConstraint("tenant_id", "name", name="uq_role_tenant_name"),
    )
    op.create_index(op.f("ix_role_tenant_id"), "role", ["tenant_id"])

    op.create_table(
        "usuario_role",
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuario.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["role.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("usuario_id", "role_id"),
    )
    op.create_index(op.f("ix_usuario_role_tenant_id"), "usuario_role", ["tenant_id"])

    _seed_system_roles()


def _seed_system_roles() -> None:
    connection = op.get_bind()
    tenant_rows = connection.execute(
        sa.text("SELECT id FROM tenant")
    ).fetchall()

    for (tenant_id,) in tenant_rows:
        for role_name, role_data in SYSTEM_ROLES.items():
            existing = connection.execute(
                sa.text("SELECT id FROM role WHERE tenant_id = :tid AND name = :name"),
                {"tid": tenant_id, "name": role_name},
            ).fetchone()
            if existing:
                continue
            connection.execute(
                sa.text(
                    """INSERT INTO role (id, tenant_id, name, description, permissions, is_system_role)
                       VALUES (:id, :tid, :name, :desc, :perms::jsonb, :sys)"""
                ),
                {
                    "id": str(uuid.uuid4()),
                    "tid": str(tenant_id),
                    "name": role_name,
                    "desc": role_data["description"],
                    "perms": json.dumps(role_data["permissions"]),
                    "sys": True,
                },
            )


def downgrade() -> None:
    op.drop_index(op.f("ix_usuario_role_tenant_id"), table_name="usuario_role")
    op.drop_table("usuario_role")
    op.drop_index(op.f("ix_role_tenant_id"), table_name="role")
    op.drop_table("role")
