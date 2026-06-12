import enum

from sqlalchemy import Column, Enum, ForeignKey, String, UUID

from app.core.database import Base
from app.models._enum_utils import enum_values
from app.models.mixins import BaseModelMixin


class TipoEvaluacion(str, enum.Enum):
    PARCIAL = "Parcial"
    TP = "TP"
    COLOQUIO = "Coloquio"
    RECUPERATORIO = "Recuperatorio"


class Evaluacion(Base, BaseModelMixin):
    __tablename__ = "evaluacion"

    materia_id = Column(
        UUID(as_uuid=True),
        ForeignKey("materia.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    cohorte_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cohorte.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    tipo = Column(
        Enum(TipoEvaluacion, name="tipo_evaluacion", values_callable=enum_values),
        nullable=False,
    )
    instancia = Column(String(255), nullable=False)
