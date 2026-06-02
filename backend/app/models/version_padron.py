from sqlalchemy import Boolean, Column, ForeignKey, String, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class VersionPadron(Base, BaseModelMixin):
    __tablename__ = "version_padron"

    materia_id = Column(
        UUID(as_uuid=True),
        ForeignKey("materia.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    cohorte_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cohorte.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    activa = Column(Boolean, default=True, nullable=False)
    creada_por = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="RESTRICT"),
        nullable=False,
    )

    entradas = relationship("EntradaPadron", back_populates="version", cascade="all, delete-orphan")
