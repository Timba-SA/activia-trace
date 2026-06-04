import uuid
from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import EstadoReserva, TipoEvaluacion


class TurnoDisponibleCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fecha: date
    hora: time
    cupo_total: int = Field(..., ge=1)


class TurnoDisponibleResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    fecha: date
    hora: time
    cupo_total: int
    cupos_restantes: int


class EvaluacionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    tipo: TipoEvaluacion
    instancia: str = Field(..., min_length=1, max_length=255)
    turnos: list[TurnoDisponibleCreate] = Field(..., min_length=1)


class EvaluacionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tipo: TipoEvaluacion | None = None
    instancia: str | None = Field(default=None, min_length=1, max_length=255)
    turnos: list[TurnoDisponibleCreate] | None = None


class EvaluacionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    tipo: TipoEvaluacion
    instancia: str
    turnos: list[TurnoDisponibleResponse] = []
    created_at: datetime
    updated_at: datetime


class EvaluacionListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[EvaluacionResponse]
    total: int
    pages: int


class ReservaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    turno_id: uuid.UUID


class ReservaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    evaluacion_id: uuid.UUID
    alumno_id: uuid.UUID
    turno_id: uuid.UUID
    fecha_hora: datetime
    estado: EstadoReserva


class ReservaCancelResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str


class ResultadoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alumno_id: uuid.UUID
    nota_final: str = Field(..., min_length=1)


class ResultadoBatchCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[ResultadoCreate] = Field(..., min_length=1)


class ResultadoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    evaluacion_id: uuid.UUID
    alumno_id: uuid.UUID
    nota_final: str


class ConvocatoriaAlumnoImport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alumno_ids: list[uuid.UUID] = Field(..., min_length=1)


class MetricasResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_alumnos: int
    instancias_activas: int
    reservas_activas: int
    notas_registradas: int


class ConvocatoriaListadoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[EvaluacionResponse]
    total: int
    pages: int
