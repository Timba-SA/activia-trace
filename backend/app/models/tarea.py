import enum

from sqlalchemy import Column, Enum, ForeignKey, Text, String, UUID
from app.core.database import Base
from app.models.mixins import BaseModelMixin


class EstadoTarea(str, enum.Enum):
    PENDIENTE = "Pendiente"
    EN_PROGRESO = "En progreso"
    RESUELTA = "Resuelta"
    CANCELADA = "Cancelada"


class Tarea(Base, BaseModelMixin):
    __tablename__ = "tarea"

    estado = Column(
        Enum(EstadoTarea, name="estado_tarea"),
        nullable=False,
        default=EstadoTarea.PENDIENTE,
    )
    asignado_a = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )
    asignado_por = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="SET NULL"),
        nullable=False,
    )
    materia_id = Column(
        UUID(as_uuid=True),
        ForeignKey("materia.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    contexto_id = Column(UUID(as_uuid=True), nullable=True)
    descripcion = Column(Text, nullable=False)
