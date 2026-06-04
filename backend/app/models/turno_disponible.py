import uuid

from sqlalchemy import Column, Date, ForeignKey, Integer, Time, UniqueConstraint, UUID

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class TurnoDisponible(Base, BaseModelMixin):
    __tablename__ = "turno_disponible"

    evaluacion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("evaluacion.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    cupo_total = Column(Integer, nullable=False)
    cupos_restantes = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "evaluacion_id", "fecha", "hora",
            name="uk_turno_evaluacion_fecha_hora",
        ),
    )

    def __init__(self, **kwargs):
        if "cupos_restantes" not in kwargs or kwargs["cupos_restantes"] is None:
            kwargs["cupos_restantes"] = kwargs.get("cupo_total", 0)
        super().__init__(**kwargs)
