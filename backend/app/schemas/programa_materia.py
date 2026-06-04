import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ProgramaMateriaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    carrera_id: uuid.UUID
    cohorte_id: uuid.UUID | None = None
    titulo: str = Field(..., min_length=1, max_length=255)
    referencia_archivo: str | None = Field(default=None, max_length=500)
    aprobado_en: date | None = None


class ProgramaMateriaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    titulo: str | None = Field(default=None, min_length=1, max_length=255)
    referencia_archivo: str | None = Field(default=None, max_length=500)
    contenido_html: str | None = None
    aprobado_en: date | None = None


class ProgramaMateriaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    materia_id: uuid.UUID
    carrera_id: uuid.UUID
    cohorte_id: uuid.UUID | None = None
    titulo: str
    referencia_archivo: str | None = None
    contenido_html: str | None = None
    version: int
    activo: bool
    aprobado_en: date | None = None
    created_at: datetime
    updated_at: datetime


class ProgramaMateriaListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[ProgramaMateriaResponse]
    total: int
    page: int
    page_size: int


class GenerarContenidoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contenido_html: str
