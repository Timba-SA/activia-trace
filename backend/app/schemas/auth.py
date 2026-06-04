import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CurrentUser(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    roles: list[str] = []
    permissions: frozenset[str] = frozenset()
    is_active: bool = True


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(..., min_length=1)


class Login2FARequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    temp_token: str
    code: str = Field(..., min_length=6, max_length=6)


class RefreshRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str
    email: EmailStr
    new_password: str = Field(..., min_length=8)


class Enroll2FARequest(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Verify2FARequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(..., min_length=6, max_length=6)


class TokenResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900


class TempTokenResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    temp_token: str
    requires_2fa: bool = True
    expires_in: int = 300


class Enroll2FAResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    secret: str
    provisioning_uri: str


class RecoveryTokenResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = "If the email exists, a recovery token has been generated"


class RecoveryTokenGeneratedResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str
    expires_in_minutes: int = 15
    message: str = "Recovery token generated (for MVP; production sends via email)"


class LogoutResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = "Logged out successfully"


class MessageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str


class ImpersonateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: uuid.UUID


class ImpersonateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_token: str
    token_type: str = "bearer"
    expires_in: int = 900
    impersonating_user_id: uuid.UUID
    target_user_id: uuid.UUID
