import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class SalarioBaseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rol: str
    monto: float
    desde: date
    hasta: date | None = None


class SalarioBaseUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    monto: float | None = None
    desde: date | None = None
    hasta: date | None = None


class SalarioBaseResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    rol: str
    monto: float
    desde: date
    hasta: date | None = None
    created_at: datetime
    updated_at: datetime
