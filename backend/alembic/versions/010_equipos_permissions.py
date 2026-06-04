"""seed equipos:asignar and equipos:ver permissions

Revision ID: 010
Revises: 009
Create Date: 2026-06-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "010"
down_revision: str | None = "009"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions || :perm::jsonb
               WHERE name IN ('COORDINADOR', 'ADMIN')
               AND NOT (permissions ? :perm_str)"""
        ).bindparams(perm=sa.text('\'["equipos:asignar"]\'::jsonb'), perm_str="equipos:asignar"),
    )

    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions || :perm::jsonb
               WHERE name IN ('PROFESOR', 'TUTOR', 'NEXO', 'COORDINADOR', 'ADMIN')
               AND NOT (permissions ? :perm_str)"""
        ).bindparams(perm=sa.text('\'["equipos:ver"]\'::jsonb'), perm_str="equipos:ver"),
    )


def downgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions - :perm_str
               WHERE permissions ? :perm_str"""
        ).bindparams(perm_str="equipos:asignar"),
    )

    connection.execute(
        sa.text(
            """UPDATE role
               SET permissions = permissions - :perm_str
               WHERE permissions ? :perm_str"""
        ).bindparams(perm_str="equipos:ver"),
    )
