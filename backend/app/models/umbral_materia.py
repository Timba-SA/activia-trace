from sqlalchemy import Column, Float, ForeignKey, String, UUID
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class UmbralMateria(Base, BaseModelMixin):
    __tablename__ = "umbral_materia"

    materia_id = Column(
        UUID(as_uuid=True),
        ForeignKey("materia.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    cohorte_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cohorte.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    umbral_pct = Column(Float, nullable=False, default=60.0)
    valores_aprobados = Column(JSONB, nullable=False, default=lambda: ["Aprobado", "Promocionado"])
