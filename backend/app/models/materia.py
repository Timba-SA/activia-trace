from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint, UUID

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Materia(Base, BaseModelMixin):
    __tablename__ = "materia"

    carrera_id = Column(
        UUID(as_uuid=True),
        ForeignKey("carrera.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    codigo = Column(String(50), nullable=False)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(String(1000), nullable=True)
    carga_horaria = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("tenant_id", "codigo", name="uk_materia_codigo_tenant"),
    )
