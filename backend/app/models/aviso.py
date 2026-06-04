import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text, UUID
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class AlcanceAviso(str, enum.Enum):
    GLOBAL = "Global"
    POR_MATERIA = "PorMateria"
    POR_COHORTE = "PorCohorte"
    POR_ROL = "PorRol"


class SeveridadAviso(str, enum.Enum):
    INFO = "Info"
    ADVERTENCIA = "Advertencia"
    CRITICO = "Critico"


class Aviso(Base, BaseModelMixin):
    __tablename__ = "aviso"

    alcance = Column(
        Enum(AlcanceAviso, name="alcance_aviso"),
        nullable=False,
    )
    materia_id = Column(
        UUID(as_uuid=True),
        ForeignKey("materia.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    cohorte_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cohorte.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    rol_destino = Column(
        String(100),
        nullable=True,
    )
    severidad = Column(
        Enum(SeveridadAviso, name="severidad_aviso"),
        nullable=False,
    )
    titulo = Column(String(255), nullable=False)
    cuerpo = Column(Text, nullable=False)
    inicio_en = Column(DateTime(timezone=True), nullable=False)
    fin_en = Column(DateTime(timezone=True), nullable=False)
    orden = Column(Integer, default=0, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    requiere_ack = Column(Boolean, default=False, nullable=False)
