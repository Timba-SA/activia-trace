import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CohorteCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    carrera_id: uuid.UUID
    nombre: str = Field(..., min_length=1, max_length=255)
    anio: int = Field(..., ge=1900, le=2150)


class CohorteUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str | None = Field(default=None, min_length=1, max_length=255)
    anio: int | None = Field(default=None, ge=1900, le=2150)
    is_active: bool | None = None


class CohorteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    carrera_id: uuid.UUID
    nombre: str
    anio: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class CohorteListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[CohorteResponse]
    total: int
    pages: int
