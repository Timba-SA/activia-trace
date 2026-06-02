import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CarreraCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    codigo: str = Field(..., min_length=1, max_length=50)
    nombre: str = Field(..., min_length=1, max_length=255)
    descripcion: str | None = Field(default=None, max_length=1000)
    duracion_anios: int | None = None


class CarreraUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str | None = Field(default=None, min_length=1, max_length=255)
    descripcion: str | None = Field(default=None, max_length=1000)
    duracion_anios: int | None = None
    is_active: bool | None = None


class CarreraResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    codigo: str
    nombre: str
    descripcion: str | None = None
    duracion_anios: int | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class CarreraListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[CarreraResponse]
    total: int
    pages: int
