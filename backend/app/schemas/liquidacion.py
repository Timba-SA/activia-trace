import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LiquidacionCalcularRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cohorte_id: uuid.UUID
    periodo: str


class LiquidacionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    cohorte_id: uuid.UUID
    periodo: str
    usuario_id: uuid.UUID
    rol: str
    comisiones: list
    monto_base: float
    monto_plus: float
    total: float
    es_nexo: bool
    excluido_por_factura: bool
    estado: str
    created_at: datetime
    updated_at: datetime


class LiquidacionCerrarResponse(LiquidacionResponse):
    pass


class LiquidacionHistorialResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[LiquidacionResponse]
    total: int
    page: int
    page_size: int


class LiquidacionListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[LiquidacionResponse]
    total: int
    page: int
    page_size: int


class ExportarRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cohorte_id: uuid.UUID
    periodo: str
