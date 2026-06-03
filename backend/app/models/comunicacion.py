from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, UUID
from sqlalchemy.orm import Mapped

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Comunicacion(Base, BaseModelMixin):
    __tablename__ = "comunicacion"

    enviado_por_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )
    materia_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("materia.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    cohorte_id: Mapped[UUID | None] = Column(
        UUID(as_uuid=True),
        ForeignKey("cohorte.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    lote_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    destinatario: Mapped[str] = Column(
        String(255),
        nullable=False,
    )
    asunto: Mapped[str] = Column(
        String(255),
        nullable=False,
    )
    cuerpo: Mapped[str] = Column(
        Text,
        nullable=False,
    )
    estado: Mapped[str] = Column(
        String(20),
        nullable=False,
        default="Pendiente",
        index=True,
    )
    requiere_aprobacion: Mapped[bool] = Column(
        Boolean,
        nullable=False,
        default=False,
    )
    error_msg: Mapped[str | None] = Column(
        Text,
        nullable=True,
    )
    enviado_at: Mapped[datetime | None] = Column(
        DateTime(timezone=True),
        nullable=True,
    )
