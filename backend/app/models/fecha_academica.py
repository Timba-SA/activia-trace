from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text, Time, UUID

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class FechaAcademica(Base, BaseModelMixin):
    __tablename__ = "fecha_academica"

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
    tipo = Column(String(50), nullable=False, index=True)
    numero = Column(Integer, nullable=True)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=True)
    aula = Column(String(100), nullable=True)
    observaciones = Column(Text, nullable=True)
