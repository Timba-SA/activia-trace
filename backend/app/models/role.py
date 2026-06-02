from sqlalchemy import Boolean, Column, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Role(Base, BaseModelMixin):
    __tablename__ = "role"

    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    permissions = Column(JSONB, nullable=False, default=list)
    is_system_role = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_role_tenant_name"),
    )
