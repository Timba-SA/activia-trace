import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    cohorte_id: uuid.UUID | None = None
    destinatario_entrada_ids: list[uuid.UUID] = Field(..., min_length=1)
    asunto_template: str = Field(..., min_length=1)
    cuerpo_template: str = Field(..., min_length=1)


class PreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asunto_renderizado: str
    cuerpo_renderizado: str
    alumno_nombre: str


class EnvioRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    cohorte_id: uuid.UUID | None = None
    destinatario_entrada_ids: list[uuid.UUID] = Field(..., min_length=1)
    asunto: str = Field(..., min_length=1)
    cuerpo: str = Field(..., min_length=1)


class EnvioResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lote_id: str
    total: int
    estado: str  # "encolado" | "aprobacion_pendiente"


class EstadoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lote_id: str
    total: int
    pendientes: int
    enviando: int
    enviados: int
    errores: int
    cancelados: int


class AprobarResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lote_id: str
    total_aprobados: int


class CancelarResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lote_id: str
    total_cancelados: int
