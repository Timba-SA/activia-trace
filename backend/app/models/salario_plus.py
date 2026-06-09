from sqlalchemy import Column, Date, Integer, Numeric, String, Text

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class SalarioPlus(Base, BaseModelMixin):
    __tablename__ = "salario_plus"

    grupo = Column(String(50), nullable=False, index=True)
    rol = Column(String(20), nullable=False)
    descripcion = Column(Text, nullable=True)
    monto = Column(Numeric(12, 2), nullable=False)
    tope_acumulacion = Column(Integer, nullable=True)
    desde = Column(Date, nullable=False)
    hasta = Column(Date, nullable=True)
