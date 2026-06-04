import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MensajeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    destinatario_id: uuid.UUID
    asunto: str = Field(..., min_length=1, max_length=255)
    cuerpo: str = Field(..., min_length=1)


class MensajeResponder(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cuerpo: str = Field(..., min_length=1)


class MensajeOut(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    remitente_id: uuid.UUID
    destinatario_id: uuid.UUID
    hilo_id: uuid.UUID | None = None
    asunto: str
    cuerpo: str
    leido: bool
    created_at: datetime


class MensajeListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[MensajeOut]
    total: int
    page: int = 1
    page_size: int = 20
