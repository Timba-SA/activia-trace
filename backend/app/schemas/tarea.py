import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.tarea import EstadoTarea


class TareaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asignado_a: uuid.UUID
    materia_id: uuid.UUID | None = None
    contexto_id: uuid.UUID | None = None
    descripcion: str = Field(..., min_length=1)


class TareaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estado: EstadoTarea | None = None
    asignado_a: uuid.UUID | None = None
    descripcion: str | None = Field(default=None, min_length=1)


class TareaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    estado: EstadoTarea
    asignado_a: uuid.UUID
    asignado_por: uuid.UUID
    materia_id: uuid.UUID | None = None
    contexto_id: uuid.UUID | None = None
    descripcion: str
    created_at: datetime
    updated_at: datetime


class TareaListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[TareaResponse]
    total: int
    page: int
    page_size: int


class ComentarioTareaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    texto: str = Field(..., min_length=1)


class ComentarioTareaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tarea_id: uuid.UUID
    autor_id: uuid.UUID
    texto: str
    creado_at: datetime
