import uuid
from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field


class FechaAcademicaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    tipo: str = Field(..., pattern=r"^(Parcial|TP|Coloquio|Recuperatorio)$")
    numero: int | None = None
    fecha: date
    hora: time | None = None
    aula: str | None = Field(default=None, max_length=100)
    observaciones: str | None = None


class FechaAcademicaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tipo: str | None = Field(default=None, pattern=r"^(Parcial|TP|Coloquio|Recuperatorio)$")
    numero: int | None = None
    fecha: date | None = None
    hora: time | None = None
    aula: str | None = Field(default=None, max_length=100)
    observaciones: str | None = None


class FechaAcademicaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    tipo: str
    numero: int | None = None
    fecha: date
    hora: time | None = None
    aula: str | None = None
    observaciones: str | None = None
    created_at: datetime
    updated_at: datetime


class FechaAcademicaListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[FechaAcademicaResponse]
    total: int
    page: int
    page_size: int
