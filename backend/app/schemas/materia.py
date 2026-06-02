import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MateriaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    carrera_id: uuid.UUID | None = None
    codigo: str = Field(..., min_length=1, max_length=50)
    nombre: str = Field(..., min_length=1, max_length=255)
    descripcion: str | None = Field(default=None, max_length=1000)
    carga_horaria: int | None = None


class MateriaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str | None = Field(default=None, min_length=1, max_length=255)
    descripcion: str | None = Field(default=None, max_length=1000)
    carga_horaria: int | None = None
    is_active: bool | None = None


class MateriaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    carrera_id: uuid.UUID | None = None
    codigo: str
    nombre: str
    descripcion: str | None = None
    carga_horaria: int | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class MateriaListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[MateriaResponse]
    total: int
    pages: int
