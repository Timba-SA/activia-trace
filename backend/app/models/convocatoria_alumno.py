from sqlalchemy import Column, ForeignKey, UniqueConstraint, UUID

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class ConvocatoriaAlumno(Base, BaseModelMixin):
    __tablename__ = "convocatoria_alumno"

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

    __table_args__ = (
        UniqueConstraint(
            "evaluacion_id", "alumno_id",
            name="uk_convocatoria_evaluacion_alumno",
        ),
    )
