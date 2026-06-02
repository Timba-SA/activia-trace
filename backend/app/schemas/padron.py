import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PadronFileUpload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    cohorte_id: uuid.UUID


class PadronEntryPreview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    legajo: str
    nombre_completo: str
    email: str
    estado: str = "activo"
    datos_extra: dict | None = None


class PadronPreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    total_rows: int
    entries: list[PadronEntryPreview]
    preview_hash: str


class PadronConfirmRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    preview_hash: str
    entries: list[PadronEntryPreview]


class PadronConfirmResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version_id: uuid.UUID
    total_entradas: int
    activa: bool


class VersionPadronResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    activa: bool
    creada_por: uuid.UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class VersionPadronListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[VersionPadronResponse]
    total: int
    pages: int


class EntradaPadronResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    version_padron_id: uuid.UUID
    tenant_id: uuid.UUID
    usuario_id: uuid.UUID | None = None
    legajo: str
    nombre_completo: str
    email: str
    estado: str
    datos_extra: dict | None = None
    created_at: datetime
    updated_at: datetime


class EntradaPadronListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[EntradaPadronResponse]
    total: int
    pages: int
