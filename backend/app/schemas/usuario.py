import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class UsuarioUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str | None = Field(default=None, min_length=1, max_length=255)
    apellido: str | None = Field(default=None, min_length=1, max_length=255)
    dni: str | None = None
    cuil: str | None = None
    telefono: str | None = Field(default=None, max_length=50)
    direccion: str | None = Field(default=None, max_length=500)
    fecha_nacimiento: date | None = None
    legajo: str | None = Field(default=None, max_length=50)
    cbu: str | None = None
    is_active: bool | None = None


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    nombre: str | None = None
    apellido: str | None = None
    legajo: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UsuarioDetalleResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    nombre: str | None = None
    apellido: str | None = None
    legajo: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    dni: str | None = None
    cuil: str | None = None
    telefono: str | None = None
    direccion: str | None = None
    fecha_nacimiento: date | None = None
    cbu: str | None = None


class UsuarioListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[UsuarioResponse]
    total: int
    pages: int


class PerfilOut(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    nombre: str | None = None
    apellido: str | None = None
    email: str
    dni: str | None = None
    cuil: str | None = None
    telefono: str | None = None
    direccion: str | None = None
    fecha_nacimiento: str | None = None
    legajo: str | None = None
    cbu: str | None = None


class PerfilUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str | None = Field(default=None, min_length=1, max_length=255)
    apellido: str | None = Field(default=None, min_length=1, max_length=255)
    email: str | None = None
    dni: str | None = None
    telefono: str | None = Field(default=None, max_length=50)
    direccion: str | None = Field(default=None, max_length=500)
    fecha_nacimiento: str | None = None
    legajo: str | None = Field(default=None, max_length=50)
    cbu: str | None = None
