import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.guardia import DiaSemanaGuardia, EstadoGuardia


class GuardiaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asignacion_id: uuid.UUID
    materia_id: uuid.UUID
    carrera_id: uuid.UUID
    cohorte_id: uuid.UUID
    dia: DiaSemanaGuardia
    horario: str = Field(..., min_length=1, max_length=50)
    estado: EstadoGuardia = EstadoGuardia.PENDIENTE
    comentarios: str | None = Field(default=None, max_length=1000)


class GuardiaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estado: EstadoGuardia


class GuardiaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    asignacion_id: uuid.UUID
    materia_id: uuid.UUID
    carrera_id: uuid.UUID
    cohorte_id: uuid.UUID
    dia: DiaSemanaGuardia
    horario: str
    estado: EstadoGuardia
    comentarios: str | None = None
    creada_at: datetime


class GuardiaListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[GuardiaResponse]
    total: int
    pages: int
