import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class MateriaGrupoPlusCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    grupo: str
    desde: date
    hasta: date | None = None


class MateriaGrupoPlusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    grupo: str | None = None
    desde: date | None = None
    hasta: date | None = None


class MateriaGrupoPlusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    materia_id: uuid.UUID
    grupo: str
    desde: date
    hasta: date | None = None
    created_at: datetime
    updated_at: datetime
