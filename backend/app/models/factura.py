from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Text, UUID, func

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Factura(Base, BaseModelMixin):
    __tablename__ = "factura"

    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    periodo = Column(String(7), nullable=False)
    detalle = Column(Text, nullable=True)
    referencia_archivo = Column(String(255), nullable=False)
    tamano_kb = Column(Numeric(10, 2), nullable=True)
    estado = Column(String(10), nullable=False, default="Pendiente")
    cargada_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    abonada_at = Column(DateTime(timezone=True), nullable=True)
