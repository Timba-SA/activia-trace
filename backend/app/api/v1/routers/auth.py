import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.rate_limiter import RateLimiter
from app.repositories.auth_repository import (
    RecoveryTokenRepository,
    SesionRepository,
    UsuarioRepository,
)
from app.schemas.auth import (
    CurrentUser,
    Enroll2FAResponse,
    Enroll2FARequest,
    ForgotPasswordRequest,
    Login2FARequest,
    LoginRequest,
    LogoutResponse,
    MessageResponse,
    RecoveryTokenGeneratedResponse,
    RecoveryTokenResponse,
    RefreshRequest,
    ResetPasswordRequest,
    TempTokenResponse,
    TokenResponse,
    Verify2FARequest,
)
from app.services.auth_service import AuthService
from app.services.totp_service import TOTPService

router = APIRouter(prefix="/api/auth", tags=["auth"])
rate_limiter = RateLimiter()
totp_service = TOTPService()


def _build_auth_service(db: AsyncSession, tenant_id: uuid.UUID) -> AuthService:
    return AuthService(
        user_repo=UsuarioRepository(db, tenant_id),
        sesion_repo=SesionRepository(db),
        recovery_token_repo=RecoveryTokenRepository(db),
    )


@router.post("/login")
async def login(
    body: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"{client_ip}:{body.email}"
    allowed = await rate_limiter.check(rate_key)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Try again later.",
            headers={"Retry-After": "60"},
        )

    tenant_id = uuid.UUID(int=0)
    service = _build_auth_service(db, tenant_id)
    result = await service.login(body.email, body.password)

    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])

    if result.get("requires_2fa"):
        return TempTokenResponse(
            temp_token=result["temp_token"],
            requires_2fa=True,
            expires_in=result["expires_in"],
        )

    return TokenResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        token_type="bearer",
        expires_in=result["expires_in"],
    )


@router.post("/login/2fa")
async def login_2fa(
    body: Login2FARequest,
    db: AsyncSession = Depends(get_db),
):
    tenant_id = uuid.UUID(int=0)
    service = _build_auth_service(db, tenant_id)
    result = await service.verify_2fa(body.temp_token, body.code)

    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])

    return TokenResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        token_type="bearer",
        expires_in=result["expires_in"],
    )


@router.post("/refresh")
async def refresh(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    tenant_id = uuid.UUID(int=0)
    service = _build_auth_service(db, tenant_id)
    result = await service.refresh(body.refresh_token)

    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])

    return TokenResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        token_type="bearer",
        expires_in=result["expires_in"],
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    tenant_id = current_user.tenant_id
    service = _build_auth_service(db, tenant_id)
    await service.logout(body.refresh_token)
    return LogoutResponse()


@router.post("/forgot")
async def forgot_password(
    body: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    tenant_id = uuid.UUID(int=0)
    service = _build_auth_service(db, tenant_id)
    result = await service.forgot_password(body.email)

    if result is None:
        return RecoveryTokenResponse()

    return RecoveryTokenGeneratedResponse(
        token=result["token"],
        expires_in_minutes=result["expires_in_minutes"],
    )


@router.post("/reset", response_model=MessageResponse)
async def reset_password(
    body: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    tenant_id = uuid.UUID(int=0)
    service = _build_auth_service(db, tenant_id)
    result = await service.reset_password(body.token, body.email, body.new_password)

    if result is not None:
        raise HTTPException(status_code=400, detail=result["error"])

    return MessageResponse(message="Password reset successfully")


@router.post("/2fa/enroll", response_model=Enroll2FAResponse)
async def enroll_2fa(
    body: Enroll2FARequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    user_repo = UsuarioRepository(db, current_user.tenant_id)
    user = await user_repo.get(current_user.id, skip_tenant_scope=True)

    if user.is_2fa_enabled:
        raise HTTPException(status_code=409, detail="2FA is already enabled")

    secret, encrypted_secret, provisioning_uri = totp_service.generate_secret()
    await user_repo.set_2fa_secret(user.id, encrypted_secret)

    return Enroll2FAResponse(secret=secret, provisioning_uri=provisioning_uri)


@router.post("/2fa/verify", response_model=MessageResponse)
async def verify_2fa(
    body: Verify2FARequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    user_repo = UsuarioRepository(db, current_user.tenant_id)
    user = await user_repo.get(current_user.id, skip_tenant_scope=True)

    if not user.totp_secret:
        raise HTTPException(status_code=400, detail="No TOTP secret enrolled")

    if not totp_service.verify_code(user.totp_secret, body.code):
        raise HTTPException(status_code=400, detail="Invalid TOTP code")

    await user_repo.enable_2fa(user.id)
    return MessageResponse(message="2FA enabled successfully")


@router.post("/2fa/disable", response_model=MessageResponse)
async def disable_2fa(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    user_repo = UsuarioRepository(db, current_user.tenant_id)
    user = await user_repo.get(current_user.id, skip_tenant_scope=True)

    if not user.is_2fa_enabled:
        raise HTTPException(status_code=400, detail="2FA is not enabled")

    await user_repo.clear_2fa(user.id)
    return MessageResponse(message="2FA disabled successfully")
