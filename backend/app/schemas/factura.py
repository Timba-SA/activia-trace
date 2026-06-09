import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FacturaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    usuario_id: uuid.UUID
    periodo: str
    detalle: str | None = None
    referencia_archivo: str
    tamano_kb: float | None = None


class FacturaEstadoUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estado: str


class FacturaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    usuario_id: uuid.UUID
    periodo: str
    detalle: str | None = None
    referencia_archivo: str
    tamano_kb: float | None = None
    estado: str
    cargada_at: datetime
    abonada_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class FacturaListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[FacturaResponse]
    total: int
    page: int
    page_size: int
