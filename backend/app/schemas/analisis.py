import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator


class AlumnoAtrasadoItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entrada_padron_id: uuid.UUID
    legajo: str
    nombre_completo: str
    actividades_faltantes: list[str]
    actividades_bajo_umbral: list[str]
    total_actividades: int
    aprobadas_count: int


class AtrasadosResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[AlumnoAtrasadoItem]
    total: int


class RankingEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entrada_padron_id: uuid.UUID
    legajo: str
    nombre_completo: str
    aprobadas_count: int


class RankingResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[RankingEntry]
    total: int


class ReporteRapidoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    total_alumnos: int
    evaluados: int
    atrasados: int
    sin_atrasos: int
    pendientes_correccion: int
    pct_atrasados: float
    pct_evaluados: float


class NotasFinalesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    grupos: dict[str, list[str]]


class NotaFinalEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entrada_padron_id: uuid.UUID
    legajo: str
    nombre_completo: str
    grupos: dict[str, float | None]
    nota_final: float | None


class NotasFinalesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[NotaFinalEntry]
    total: int


class MonitorFiltros(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    alumno: str | None = None
    email: str | None = None
    comision: str | None = None
    regional: str | None = None
    actividad: str | None = None
    min_completion: float | None = None
    from_date: date | None = None
    to_date: date | None = None
    page: int = 1
    limit: int = 20

    @field_validator("page")
    @classmethod
    def page_must_be_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("page must be >= 1")
        return v

    @field_validator("limit")
    @classmethod
    def limit_must_be_in_range(cls, v: int) -> int:
        if v < 1 or v > 100:
            raise ValueError("limit must be between 1 and 100")
        return v

    @field_validator("from_date")
    @classmethod
    def from_date_required_for_admin(cls, v: date | None) -> date | None:
        return v

    @field_validator("to_date")
    @classmethod
    def to_date_required_for_admin(cls, v: date | None) -> date | None:
        return v


class MonitorFiltrosCoordinacion(MonitorFiltros):
    @field_validator("from_date", "to_date")
    @classmethod
    def validate_date_range(cls, v: date | None) -> date | None:
        return v


class MonitorEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entrada_padron_id: uuid.UUID
    legajo: str
    nombre_completo: str
    email: str
    actividad: str
    calificacion: str | None = None
    aprobado: bool | None = None
    es_numerica: bool | None = None
    tiene_calificacion: bool
    tiene_finalizacion: bool


class MonitorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[MonitorEntry]
    total: int
    page: int
    limit: int
    pages: int


class EntregasSinCorregirItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entrada_padron_id: uuid.UUID
    legajo: str
    nombre_completo: str
    email: str
    actividad_nombre: str
    materia_id: uuid.UUID
    cohorte_id: uuid.UUID


class EntregasSinCorregirResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[EntregasSinCorregirItem]
    total: int
