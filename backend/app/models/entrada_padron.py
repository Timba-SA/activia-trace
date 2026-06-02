from sqlalchemy import Column, ForeignKey, String, Text, UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class EntradaPadron(Base, BaseModelMixin):
    __tablename__ = "entrada_padron"

    version_padron_id = Column(
        UUID(as_uuid=True),
        ForeignKey("version_padron.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    legajo = Column(String(50), nullable=False)
    nombre_completo = Column(String(500), nullable=False)
    email = Column(Text, nullable=False)
    estado = Column(String(50), nullable=False, default="activo")
    datos_extra = Column(JSONB, nullable=True)

    version = relationship("VersionPadron", back_populates="entradas")
