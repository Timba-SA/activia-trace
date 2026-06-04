from sqlalchemy import Column, ForeignKey, Text, UUID

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class ResultadoEvaluacion(Base, BaseModelMixin):
    __tablename__ = "resultado_evaluacion"

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
    nota_final = Column(Text, nullable=False)
