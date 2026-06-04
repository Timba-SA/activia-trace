import enum

from sqlalchemy import Column, DateTime, ForeignKey, String, Enum, func, UUID

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class EstadoGuardia(str, enum.Enum):
    PENDIENTE = "Pendiente"
    REALIZADA = "Realizada"
    CANCELADA = "Cancelada"


class DiaSemanaGuardia(str, enum.Enum):
    LUNES = "Lunes"
    MARTES = "Martes"
    MIERCOLES = "Miercoles"
    JUEVES = "Jueves"
    VIERNES = "Viernes"
    SABADO = "Sabado"
    DOMINGO = "Domingo"


class Guardia(Base, BaseModelMixin):
    __tablename__ = "guardia"

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
    carrera_id = Column(
        UUID(as_uuid=True),
        ForeignKey("carrera.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    cohorte_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cohorte.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    dia = Column(Enum(DiaSemanaGuardia, name="dia_semana_guardia"), nullable=False)
    horario = Column(String(50), nullable=False)
    estado = Column(
        Enum(EstadoGuardia, name="estado_guardia"),
        nullable=False,
        default=EstadoGuardia.PENDIENTE,
    )
    comentarios = Column(String(1000), nullable=True)
    creada_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
