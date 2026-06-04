from sqlalchemy import Boolean, Column, ForeignKey, String, Text, UUID

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Mensaje(Base, BaseModelMixin):
    __tablename__ = "mensaje"

    remitente_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    destinatario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    hilo_id = Column(UUID(as_uuid=True), nullable=True)
    asunto = Column(String(255), nullable=False)
    cuerpo = Column(Text, nullable=False)
    leido = Column(Boolean, default=False, nullable=False)
