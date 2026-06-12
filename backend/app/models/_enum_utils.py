"""Utility to bridge SQLAlchemy Enum with str mixin enums.

SQLAlchemy 2.0 uses .name by default for storing enum members,
even for str mixin enums. But PostgreSQL ENUMs are created with
.value strings in migrations. This module provides the callable.

Usage::

    from app.models._enum_utils import enum_values

    estado = Column(
        Enum(EstadoInstancia, name="estado_instancia", values_callable=enum_values),
        nullable=False,
        ...
    )
"""


def enum_values(enum_class: type) -> list[str]:
    """Return .value for each member of a str enum.

    Args:
        enum_class: A ``str, enum.Enum`` subclass.

    Returns:
        List of ``.value`` strings for each member.
    """
    return [m.value for m in enum_class]
