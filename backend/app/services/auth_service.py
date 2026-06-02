import uuid

from datetime import datetime, timedelta, timezone

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_temp_token,
    decode_token,
    generate_refresh_token,
    hash_password,
    verify_password,
)
from app.repositories.auth_repository import (
    RecoveryTokenRepository,
    SesionRepository,
    UsuarioRepository,
)


class AuthService:
    def __init__(
        self,
        user_repo: UsuarioRepository,
        sesion_repo: SesionRepository,
        recovery_token_repo: RecoveryTokenRepository,
    ) -> None:
        self._user_repo = user_repo
        self._sesion_repo = sesion_repo
        self._recovery_token_repo = recovery_token_repo
        self._settings = get_settings()

    async def login(self, email: str, password: str) -> dict:
        user = await self._user_repo.find_by_email_skip_tenant(email)
        if user is None or not verify_password(password, user.hashed_password):
            return {"error": "Invalid email or password"}

        if not user.is_active:
            return {"error": "Invalid email or password"}

        if user.is_2fa_enabled:
            temp_token = create_temp_token(user.id, user.tenant_id)
            return {
                "temp_token": temp_token,
                "requires_2fa": True,
                "expires_in": 300,
            }

        user_data = {
            "sub": str(user.id),
            "tenant_id": str(user.tenant_id),
            "roles": [],
        }
        access_token = create_access_token(user_data)
        raw_refresh, refresh_hash = generate_refresh_token()
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=self._settings.refresh_token_expire_days
        )
        await self._sesion_repo.create(user.id, refresh_hash, expires_at)

        return {
            "access_token": access_token,
            "refresh_token": raw_refresh,
            "token_type": "bearer",
            "expires_in": self._settings.access_token_expire_minutes * 60,
        }

    async def verify_2fa(self, temp_token: str, code: str) -> dict:
        try:
            payload = decode_token(temp_token)
        except ValueError:
            return {"error": "Invalid or expired temp_token"}

        if not payload.get("pending_2fa"):
            return {"error": "Invalid or expired temp_token"}

        user_id = uuid.UUID(payload["sub"])
        tenant_id = uuid.UUID(payload["tenant_id"])

        try:
            user = await self._user_repo.get(user_id, skip_tenant_scope=True)
        except Exception:
            return {"error": "Invalid or expired temp_token"}

        if not user.is_2fa_enabled or not user.totp_secret:
            return {"error": "2FA not configured for this user"}

        from app.services.totp_service import TOTPService

        totp_service = TOTPService()
        if not totp_service.verify_code(user.totp_secret, code):
            return {"error": "Invalid TOTP code"}

        user_data = {
            "sub": str(user.id),
            "tenant_id": str(user.tenant_id),
            "roles": [],
        }
        access_token = create_access_token(user_data)
        raw_refresh, refresh_hash = generate_refresh_token()
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=self._settings.refresh_token_expire_days
        )
        await self._sesion_repo.create(user.id, refresh_hash, expires_at)

        return {
            "access_token": access_token,
            "refresh_token": raw_refresh,
            "token_type": "bearer",
            "expires_in": self._settings.access_token_expire_minutes * 60,
        }

    async def refresh(self, raw_token: str) -> dict:
        import hashlib

        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        sesion = await self._sesion_repo.find_by_hash(token_hash)

        if sesion is None:
            return {"error": "Invalid refresh token"}

        if sesion.is_revoked:
            await self._sesion_repo.revoke_all_for_user(sesion.user_id)
            return {"error": "Refresh token revoked — all sessions invalidated"}

        if sesion.expires_at and sesion.expires_at < datetime.now(timezone.utc):
            return {"error": "Refresh token expired"}

        await self._sesion_repo.revoke(sesion.id)

        user = await self._user_repo.get(sesion.user_id, skip_tenant_scope=True)

        user_data = {
            "sub": str(user.id),
            "tenant_id": str(user.tenant_id),
            "roles": [],
        }
        access_token = create_access_token(user_data)
        raw_new_refresh, refresh_hash = generate_refresh_token()
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=self._settings.refresh_token_expire_days
        )
        await self._sesion_repo.create(user.id, refresh_hash, expires_at)

        return {
            "access_token": access_token,
            "refresh_token": raw_new_refresh,
            "token_type": "bearer",
            "expires_in": self._settings.access_token_expire_minutes * 60,
        }

    async def logout(self, raw_token: str) -> None:
        import hashlib

        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        sesion = await self._sesion_repo.find_by_hash(token_hash)
        if sesion is not None and not sesion.is_revoked:
            await self._sesion_repo.revoke(sesion.id)

    async def forgot_password(self, email: str) -> dict | None:
        user = await self._user_repo.find_by_email_skip_tenant(email)
        if user is None or not user.is_active:
            return None

        import secrets

        raw_token = secrets.token_hex(32)
        import hashlib

        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=self._settings.recovery_token_expire_minutes
        )
        await self._recovery_token_repo.create(user.id, token_hash, expires_at)

        return {
            "token": raw_token,
            "expires_in_minutes": self._settings.recovery_token_expire_minutes,
        }

    async def reset_password(self, raw_token: str, email: str, new_password: str) -> dict | None:
        import hashlib

        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        recovery_token = await self._recovery_token_repo.find_by_hash(token_hash)

        if recovery_token is None:
            return {"error": "Invalid or expired token"}

        if recovery_token.used_at is not None:
            return {"error": "Token already used"}

        if recovery_token.expires_at < datetime.now(timezone.utc):
            return {"error": "Token expired"}

        user = await self._user_repo.get(recovery_token.user_id, skip_tenant_scope=True)
        if user.email != email:
            return {"error": "Token does not match this email"}

        hashed = hash_password(new_password)
        await self._user_repo.update_password(user.id, hashed)
        await self._recovery_token_repo.mark_used(recovery_token.id)
        return None
