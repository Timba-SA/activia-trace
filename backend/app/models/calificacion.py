from sqlalchemy import Boolean, Column, ForeignKey, String, UUID
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Calificacion(Base, BaseModelMixin):
    __tablename__ = "calificacion"

    entrada_padron_id = Column(
        UUID(as_uuid=True),
        ForeignKey("entrada_padron.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    materia_id = Column(
        UUID(as_uuid=True),
        ForeignKey("materia.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    cohorte_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cohorte.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    actividad_nombre = Column(String(255), nullable=False)
    calificacion = Column(String(50), nullable=False)
    es_numerica = Column(Boolean, nullable=False, default=False)
    aprobado = Column(Boolean, nullable=False, default=False)
    origen = Column(String(50), nullable=False, default="Importado")
    metadata_json = Column(JSONB, nullable=True)
