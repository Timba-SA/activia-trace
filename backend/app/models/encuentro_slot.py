import enum

from sqlalchemy import Column, Date, ForeignKey, Integer, String, Time, Enum, UUID

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class DiaSemana(str, enum.Enum):
    LUNES = "Lunes"
    MARTES = "Martes"
    MIERCOLES = "Miercoles"
    JUEVES = "Jueves"
    VIERNES = "Viernes"
    SABADO = "Sabado"
    DOMINGO = "Domingo"


class SlotEncuentro(Base, BaseModelMixin):
    __tablename__ = "slot_encuentro"

    asignacion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("asignacion.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    materia_id = Column(
        UUID(as_uuid=True),
        ForeignKey("materia.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    titulo = Column(String(255), nullable=False)
    hora = Column(Time, nullable=False)
    dia_semana = Column(Enum(DiaSemana, name="dia_semana"), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    cant_semanas = Column(Integer, nullable=False, default=0)
    fecha_unica = Column(Date, nullable=True)
    meet_url = Column(String(500), nullable=True)
    vig_desde = Column(Date, nullable=False)
    vig_hasta = Column(Date, nullable=False)
