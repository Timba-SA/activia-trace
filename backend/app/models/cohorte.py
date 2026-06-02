from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint, UUID

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Cohorte(Base, BaseModelMixin):
    __tablename__ = "cohorte"

    carrera_id = Column(
        UUID(as_uuid=True),
        ForeignKey("carrera.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    nombre = Column(String(255), nullable=False)
    anio = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "carrera_id", "nombre",
            name="uk_cohorte_nombre_carrera_tenant",
        ),
    )
