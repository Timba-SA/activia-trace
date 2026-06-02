import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RoleCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    permissions: list[str] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    permissions: list[str] | None = None


class RoleResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    description: str | None = None
    permissions: list[str]
    is_system_role: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class RoleListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[RoleResponse]
    total: int
    pages: int


class UserRoleAssignRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role_id: uuid.UUID


class UserRoleResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None = None
    permissions: list[str]
    is_system_role: bool
