from sqlalchemy import Boolean, Column, Date, ForeignKey, Numeric, String, UUID
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base
from app.models.mixins import BaseModelMixin, TimeStampedMixin


class Liquidacion(Base, BaseModelMixin):
    __tablename__ = "liquidacion"

    cohorte_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cohorte.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    periodo = Column(String(7), nullable=False)
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    rol = Column(String(20), nullable=False)
    comisiones = Column(JSONB, nullable=False, default=list)
    monto_base = Column(Numeric(12, 2), nullable=False)
    monto_plus = Column(Numeric(12, 2), nullable=False, default=0)
    total = Column(Numeric(12, 2), nullable=False)
    es_nexo = Column(Boolean, nullable=False, default=False)
    excluido_por_factura = Column(Boolean, nullable=False, default=False)
    estado = Column(String(10), nullable=False, default="Abierta")
