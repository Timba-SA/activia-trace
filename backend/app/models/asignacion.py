from sqlalchemy import Boolean, Column, Date, ForeignKey, JSON, String, UUID, UniqueConstraint

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Asignacion(Base, BaseModelMixin):
    __tablename__ = "asignacion"

    usuario_id = Column(UUID, ForeignKey("usuario.id", ondelete="RESTRICT"), nullable=False, index=True)
    rol = Column(String(50), nullable=False)
    carrera_id = Column(UUID, ForeignKey("carrera.id", ondelete="RESTRICT"), nullable=True, index=True)
    materia_id = Column(UUID, ForeignKey("materia.id", ondelete="RESTRICT"), nullable=True, index=True)
    cohorte_id = Column(UUID, ForeignKey("cohorte.id", ondelete="RESTRICT"), nullable=True, index=True)
    responsable_id = Column(UUID, ForeignKey("usuario.id", ondelete="SET NULL"), nullable=True, index=True)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=True)
    comisiones = Column(JSON, nullable=False, default=list)
    is_active = Column(Boolean, default=True, nullable=False)
