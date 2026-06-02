import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TenantCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")
    code: str = Field(..., min_length=1, max_length=50, pattern=r"^[A-Z0-9_]+$")
    is_active: bool = Field(default=True)


class TenantUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=255)
    is_active: bool | None = None


class TenantResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class TenantListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_active: bool | None = None
    search: str | None = Field(default=None, max_length=255)
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
