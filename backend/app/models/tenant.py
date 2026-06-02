import uuid

from sqlalchemy import Boolean, Column, DateTime, String, func, UUID

from app.core.database import Base
from app.models.mixins import TimeStampedMixin


class Tenant(Base, TimeStampedMixin):
    __tablename__ = "tenant"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True, default=None)
