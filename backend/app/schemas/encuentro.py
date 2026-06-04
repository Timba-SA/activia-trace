import uuid
from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field

from app.models.encuentro_instancia import EstadoInstancia
from app.models.encuentro_slot import DiaSemana


class SlotEncuentroCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asignacion_id: uuid.UUID
    materia_id: uuid.UUID
    titulo: str = Field(..., min_length=1, max_length=255)
    hora: time
    dia_semana: DiaSemana
    fecha_inicio: date
    cant_semanas: int = Field(default=0, ge=0, le=52)
    fecha_unica: date | None = None
    meet_url: str | None = Field(default=None, max_length=500)
    vig_desde: date
    vig_hasta: date


class SlotEncuentroUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    titulo: str | None = Field(default=None, min_length=1, max_length=255)
    hora: time | None = None
    dia_semana: DiaSemana | None = None
    fecha_inicio: date | None = None
    cant_semanas: int | None = Field(default=None, ge=0, le=52)
    fecha_unica: date | None = None
    meet_url: str | None = Field(default=None, max_length=500)
    vig_desde: date | None = None
    vig_hasta: date | None = None


class SlotEncuentroResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    asignacion_id: uuid.UUID
    materia_id: uuid.UUID
    titulo: str
    hora: time
    dia_semana: DiaSemana
    fecha_inicio: date
    cant_semanas: int
    fecha_unica: date | None = None
    meet_url: str | None = None
    vig_desde: date
    vig_hasta: date
    created_at: datetime
    updated_at: datetime


class SlotEncuentroListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[SlotEncuentroResponse]
    total: int
    pages: int


class InstanciaEncuentroCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    slot_id: uuid.UUID | None = None
    fecha: date
    hora: time
    titulo: str = Field(..., min_length=1, max_length=255)
    meet_url: str | None = Field(default=None, max_length=500)


class InstanciaEncuentroUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estado: EstadoInstancia | None = None
    meet_url: str | None = Field(default=None, max_length=500)
    video_url: str | None = Field(default=None, max_length=500)
    comentario: str | None = Field(default=None, max_length=1000)


class InstanciaEncuentroResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    slot_id: uuid.UUID | None = None
    materia_id: uuid.UUID
    fecha: date
    hora: time
    titulo: str
    estado: EstadoInstancia
    meet_url: str | None = None
    video_url: str | None = None
    comentario: str | None = None
    created_at: datetime
    updated_at: datetime


class InstanciaEncuentroListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[InstanciaEncuentroResponse]
    total: int
    pages: int
