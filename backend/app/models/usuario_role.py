import uuid

from sqlalchemy import Column, DateTime, ForeignKey, PrimaryKeyConstraint, func, UUID

from app.core.database import Base


class UsuarioRole(Base):
    __tablename__ = "usuario_role"

    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="CASCADE"),
        nullable=False,
    )
    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("role.id", ondelete="CASCADE"),
        nullable=False,
    )
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenant.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        PrimaryKeyConstraint("usuario_id", "role_id"),
    )
