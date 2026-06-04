import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class AsignacionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    usuario_id: uuid.UUID
    rol: str = Field(..., min_length=1, max_length=50)
    carrera_id: uuid.UUID | None = None
    materia_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    responsable_id: uuid.UUID | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    comisiones: list[str] = Field(default_factory=list)


class AsignacionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rol: str | None = Field(default=None, min_length=1, max_length=50)
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    comisiones: list[str] | None = None
    is_active: bool | None = None


class AsignacionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    usuario_id: uuid.UUID
    rol: str
    carrera_id: uuid.UUID | None = None
    materia_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    responsable_id: uuid.UUID | None = None
    fecha_inicio: date
    fecha_fin: date | None = None
    comisiones: list[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class AsignacionListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[AsignacionResponse]
    total: int
    pages: int


# ── Equipos docentes request/response schemas ─────────────────────────────────


class AsignacionMasivaRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    usuario_ids: list[uuid.UUID]
    materia_id: uuid.UUID
    carrera_id: uuid.UUID
    cohorte_id: uuid.UUID
    rol: str = Field(..., min_length=1, max_length=50)
    responsable_id: uuid.UUID | None = None
    fecha_inicio: date
    fecha_fin: date
    comisiones: list[str] | None = None


class CloneRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    carrera_id: uuid.UUID
    cohorte_origen_id: uuid.UUID
    cohorte_destino_id: uuid.UUID
    fecha_inicio: date
    fecha_fin: date


class VigenciaUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    carrera_id: uuid.UUID
    cohorte_id: uuid.UUID
    fecha_inicio: date
    fecha_fin: date


class AsignacionDocenteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    usuario_id: uuid.UUID
    nombre: str | None = None
    apellido: str | None = None
    rol: str
    carrera_id: uuid.UUID | None = None
    materia_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    responsable_id: uuid.UUID | None = None
    fecha_inicio: date
    fecha_fin: date | None = None
    comisiones: list[str]
    is_active: bool


class AsignacionDocenteListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[AsignacionDocenteResponse]
    total: int
    pages: int


class BulkOperationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    creadas: int | None = None
    afectadas: int | None = None
