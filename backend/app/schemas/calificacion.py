import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CalificacionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    entrada_padron_id: uuid.UUID
    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    usuario_id: uuid.UUID | None = None
    actividad_nombre: str
    calificacion: str
    es_numerica: bool
    aprobado: bool
    origen: str
    metadata_json: dict | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class CalificacionListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[CalificacionResponse]
    total: int
    pages: int


class ImportPreviewColumn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actividad_nombre: str
    es_numerica: bool


class ImportPreviewRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entrada_padron_id: str
    legajo: str
    nombre_completo: str
    valores: dict[str, str]


class ImportPreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: str
    cohorte_id: str
    columns: list[ImportPreviewColumn]
    rows: list[ImportPreviewRow]
    preview_hash: str


class ImportConfirmRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    selected_activities: list[str]
    preview_hash: str
    rows: list[ImportPreviewRow]


class ImportConfirmResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_creados: int
