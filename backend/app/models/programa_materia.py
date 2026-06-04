from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Text, UniqueConstraint, UUID

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class ProgramaMateria(Base, BaseModelMixin):
    __tablename__ = "programa_materia"

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
        nullable=True,
        index=True,
    )
    titulo = Column(String(255), nullable=False)
    referencia_archivo = Column(String(500), nullable=True)
    contenido_html = Column(Text, nullable=True)
    version = Column(Integer, default=1, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    aprobado_en = Column(Date, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "materia_id", "carrera_id", "cohorte_id", "version",
            name="uq_programa_version",
        ),
    )
