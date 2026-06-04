from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Text, UUID
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class ComentarioTarea(Base, BaseModelMixin):
    __tablename__ = "comentario_tarea"

    tarea_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tarea.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    autor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )
    texto = Column(Text, nullable=False)
    creado_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
