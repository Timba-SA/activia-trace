import uuid

from sqlalchemy import Column, DateTime, ForeignKey, func, UUID
from sqlalchemy.orm import declared_attr


class TimeStampedMixin:
    """Mixin that adds created_at and updated_at timestamp columns."""

    @declared_attr
    def created_at(cls):
        return Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )


class BaseModelMixin(TimeStampedMixin):
    """Mixin for all domain entities that belong to a tenant.

    Includes UUID primary key, tenant_id FK, timestamps, and soft-delete.
    """

    @declared_attr
    def id(cls):
        return Column(
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
        )

    @declared_attr
    def tenant_id(cls):
        return Column(
            UUID(as_uuid=True),
            ForeignKey("tenant.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )

    @declared_attr
    def deleted_at(cls):
        return Column(DateTime(timezone=True), nullable=True, default=None)
