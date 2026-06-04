import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import AlcanceAviso, SeveridadAviso


class AvisoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alcance: AlcanceAviso
    materia_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    rol_destino: str | None = None
    severidad: SeveridadAviso
    titulo: str = Field(..., min_length=1, max_length=255)
    cuerpo: str = Field(..., min_length=1)
    inicio_en: datetime
    fin_en: datetime
    orden: int = 0
    activo: bool = True
    requiere_ack: bool = False


class AvisoUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alcance: AlcanceAviso | None = None
    materia_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    rol_destino: str | None = None
    severidad: SeveridadAviso | None = None
    titulo: str | None = Field(default=None, min_length=1, max_length=255)
    cuerpo: str | None = Field(default=None, min_length=1)
    inicio_en: datetime | None = None
    fin_en: datetime | None = None
    orden: int | None = None
    activo: bool | None = None
    requiere_ack: bool | None = None


class AvisoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    alcance: AlcanceAviso
    materia_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    rol_destino: str | None = None
    severidad: SeveridadAviso
    titulo: str
    cuerpo: str
    inicio_en: datetime
    fin_en: datetime
    orden: int
    activo: bool
    requiere_ack: bool
    created_at: datetime
    updated_at: datetime


class AvisoListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[AvisoResponse]
    total: int
    page: int
    page_size: int


class AckResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str


class AvisoStatsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_confirmaciones: int
