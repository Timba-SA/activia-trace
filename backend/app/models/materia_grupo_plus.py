from sqlalchemy import Column, Date, ForeignKey, String, UUID

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class MateriaGrupoPlus(Base, BaseModelMixin):
    __tablename__ = "materia_grupo_plus"

    materia_id = Column(
        UUID(as_uuid=True),
        ForeignKey("materia.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    grupo = Column(String(50), nullable=False)
    desde = Column(Date, nullable=False)
    hasta = Column(Date, nullable=True)
