import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class SalarioPlusCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    grupo: str
    rol: str
    descripcion: str | None = None
    monto: float
    tope_acumulacion: int | None = None
    desde: date
    hasta: date | None = None


class SalarioPlusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    grupo: str | None = None
    rol: str | None = None
    descripcion: str | None = None
    monto: float | None = None
    tope_acumulacion: int | None = None
    desde: date | None = None
    hasta: date | None = None


class SalarioPlusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    grupo: str
    rol: str
    descripcion: str | None = None
    monto: float
    tope_acumulacion: int | None = None
    desde: date
    hasta: date | None = None
    created_at: datetime
    updated_at: datetime
