import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UUID, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class AuditLog(Base, BaseModelMixin):
    __tablename__ = "audit_log"

    actor_id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    impersonado_id: Mapped[uuid.UUID | None] = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    materia_id: Mapped[uuid.UUID | None] = Column(
        UUID(as_uuid=True),
        ForeignKey("materia.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    fecha_hora = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    accion: Mapped[str] = Column(
        String(100),
        nullable=False,
        index=True,
    )
    detalle = Column(JSONB, nullable=True)
    filas_afectadas: Mapped[int] = Column(
        Integer,
        nullable=False,
        default=0,
    )
    ip: Mapped[str | None] = Column(
        String(45),
        nullable=True,
    )
    user_agent: Mapped[str | None] = Column(
        String(500),
        nullable=True,
    )
