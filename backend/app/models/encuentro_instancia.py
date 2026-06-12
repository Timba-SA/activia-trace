import enum

from sqlalchemy import Column, Date, ForeignKey, String, Time, Enum, UUID

from app.core.database import Base
from app.models._enum_utils import enum_values
from app.models.mixins import BaseModelMixin


class EstadoInstancia(str, enum.Enum):
    PROGRAMADO = "Programado"
    REALIZADO = "Realizado"
    CANCELADO = "Cancelado"


class InstanciaEncuentro(Base, BaseModelMixin):
    __tablename__ = "instancia_encuentro"

    slot_id = Column(
        UUID(as_uuid=True),
        ForeignKey("slot_encuentro.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    materia_id = Column(
        UUID(as_uuid=True),
        ForeignKey("materia.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    titulo = Column(String(255), nullable=False)
    estado = Column(
        Enum(EstadoInstancia, name="estado_instancia", values_callable=enum_values),
        nullable=False,
        default=EstadoInstancia.PROGRAMADO,
    )
    meet_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    comentario = Column(String(1000), nullable=True)
