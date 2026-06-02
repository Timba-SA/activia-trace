import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UmbralMateriaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    materia_id: uuid.UUID
    cohorte_id: uuid.UUID | None = None
    umbral_pct: float
    valores_aprobados: list[str]
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class UmbralMateriaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    umbral_pct: float | None = None
    valores_aprobados: list[str] | None = None


class UmbralMateriaDefaultResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    umbral_pct: float = Field(default=60.0)
    valores_aprobados: list[str] = Field(default=["Aprobado", "Promocionado"])
