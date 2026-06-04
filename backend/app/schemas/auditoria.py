from datetime import date

import uuid
from pydantic import BaseModel, ConfigDict


class MetricaAccionesPorDia(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fecha: date
    cantidad: int


class MetricaPorDocente(BaseModel):
    model_config = ConfigDict(extra="forbid")

    docente_id: uuid.UUID
    docente_nombre: str
    total: int
    detalle_por_accion: dict[str, int]


class MetricaPorDocenteListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[MetricaPorDocente]


class MetricaPorMateria(BaseModel):
    model_config = ConfigDict(extra="forbid")

    docente_id: uuid.UUID
    materia_id: uuid.UUID
    materia_nombre: str
    total: int


class MetricaPorMateriaListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[MetricaPorMateria]


class MetricaComunicaciones(BaseModel):
    model_config = ConfigDict(extra="forbid")

    docente_id: uuid.UUID
    estados: dict[str, int]


class MetricaComunicacionesListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[MetricaComunicaciones]
