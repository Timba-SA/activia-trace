from sqlalchemy import Boolean, Column, Date, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Usuario(Base, BaseModelMixin):
    __tablename__ = "usuario"

    email = Column(String(255), nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_2fa_enabled = Column(Boolean, default=False, nullable=False)
    totp_secret = Column(String(512), nullable=True)

    nombre = Column(String(255), nullable=True)
    apellido = Column(String(255), nullable=True)
    dni = Column(Text, nullable=True)
    cuil = Column(Text, nullable=True)
    telefono = Column(String(50), nullable=True)
    direccion = Column(String(500), nullable=True)
    fecha_nacimiento = Column(Date, nullable=True)
    legajo = Column(String(50), nullable=True)
    cbu = Column(Text, nullable=True)
    facturador = Column(Boolean, default=False, nullable=False)

    roles = relationship("Role", secondary="usuario_role", viewonly=True)

    __table_args__ = (
        UniqueConstraint("tenant_id", "legajo", name="uq_usuario_legajo_tenant"),
    )
