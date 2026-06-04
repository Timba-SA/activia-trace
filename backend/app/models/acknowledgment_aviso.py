import uuid

from sqlalchemy import Column, DateTime, ForeignKey, UUID, UniqueConstraint
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class AcknowledgmentAviso(Base, BaseModelMixin):
    __tablename__ = "acknowledgment_aviso"

    aviso_id = Column(
        UUID(as_uuid=True),
        ForeignKey("aviso.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    confirmado_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("aviso_id", "usuario_id", name="uq_ack_aviso_usuario"),
    )
