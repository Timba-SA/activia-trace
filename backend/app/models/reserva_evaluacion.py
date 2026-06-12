import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, UUID

from app.core.database import Base
from app.models._enum_utils import enum_values
from app.models.mixins import BaseModelMixin


class EstadoReserva(str, enum.Enum):
    ACTIVA = "Activa"
    CANCELADA = "Cancelada"


class ReservaEvaluacion(Base, BaseModelMixin):
    __tablename__ = "reserva_evaluacion"

    evaluacion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("evaluacion.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    alumno_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    turno_id = Column(
        UUID(as_uuid=True),
        ForeignKey("turno_disponible.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    fecha_hora = Column(DateTime(timezone=True), nullable=False)
    estado = Column(
        Enum(EstadoReserva, name="estado_reserva", values_callable=enum_values),
        nullable=False,
        default=EstadoReserva.ACTIVA,
    )
