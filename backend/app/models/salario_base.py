from sqlalchemy import Column, Date, Numeric, String

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class SalarioBase(Base, BaseModelMixin):
    __tablename__ = "salario_base"

    rol = Column(String(20), nullable=False, index=True)
    monto = Column(Numeric(12, 2), nullable=False)
    desde = Column(Date, nullable=False)
    hasta = Column(Date, nullable=True)
