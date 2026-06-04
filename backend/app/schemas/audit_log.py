import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuditLogCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actor_id: uuid.UUID
    tenant_id: uuid.UUID
    accion: str = Field(..., max_length=100)
    materia_id: uuid.UUID | None = None
    impersonado_id: uuid.UUID | None = None
    detalle: dict | None = None
    filas_afectadas: int = 0
    ip: str | None = Field(None, max_length=45)
    user_agent: str | None = Field(None, max_length=500)


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    actor_id: uuid.UUID
    impersonado_id: uuid.UUID | None = None
    materia_id: uuid.UUID | None = None
    fecha_hora: datetime
    accion: str
    detalle: dict | None = None
    filas_afectadas: int = 0
    ip: str | None = None
    user_agent: str | None = None


class AuditLogListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[AuditLogResponse]
    total: int
    pages: int
    limit: int
    offset: int
