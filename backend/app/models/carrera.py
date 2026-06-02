from sqlalchemy import Boolean, Column, Integer, String, UniqueConstraint

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Carrera(Base, BaseModelMixin):
    __tablename__ = "carrera"

    codigo = Column(String(50), nullable=False)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(String(1000), nullable=True)
    duracion_anios = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("tenant_id", "codigo", name="uk_carrera_codigo_tenant"),
    )
