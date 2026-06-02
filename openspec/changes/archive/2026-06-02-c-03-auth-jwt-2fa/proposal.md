## Why

C-02 established the multi-tenant foundation (Tenant model, BaseRepository, AES-256 encryption) but the system has no authentication. Every API is unprotected. C-03 implements the auth gateway: JWT-based login with Argon2id, refresh token rotation, optional 2FA TOTP, password recovery, and rate limiting. This is the security perimeter — without it, no domain feature can be built.

## What Changes

- `POST /api/auth/login` — email + password authentication with Argon2id, issues JWT access token (15 min) + refresh token with rotation
- `POST /api/auth/refresh` — rotates refresh token, emits new access/refresh pair
- `POST /api/auth/logout` — revokes current session (invalidates refresh token)
- **2FA TOTP optional** per user: enroll, verify, gate between credential validation and session issuance
- `POST /api/auth/forgot` — single-use recovery token sent by email, short expiry
- `POST /api/auth/reset` — validates recovery token, sets new password
- Rate limiting 5/60s per IP+email on login endpoint
- Dependency `get_current_user` resolving identity + tenant + roles from verified JWT
- Minimal User model (email, hashed_password, 2FA fields, is_active) for auth purposes — C-07 will expand it
- Session model for refresh token tracking and revocation
- Migrations 00X: `usuario` and `sesion` tables

## Capabilities

### New Capabilities
- `auth` — JWT-based authentication with login, refresh, logout, and `get_current_user` dependency
- `two-factor-auth` — TOTP enrollment, verification, and login gating
- `password-recovery` — forgot/reset flow with single-use tokens
- `rate-limiting` — per-IP+email rate limiting on login

### Modified Capabilities
- `app-configuration`: new settings for JWT, refresh TTL, rate-limit parameters, recovery token TTL

## Impact

- **New models**: `Usuario` (minimal), `Sesion` (refresh token tracking), `RecoveryToken` (password reset)
- **Modified files**: `core/security.py` (add JWT + Argon2), `core/dependencies.py` (add get_current_user), `core/config.py` (new settings)
- **New files**: `api/v1/routers/auth.py`, `schemas/auth.py`, `services/auth_service.py`, `repositories/auth_repository.py`
- **Dependencies**: `python-jose` and `argon2-cffi` already in pyproject.toml; add `pyotp` for TOTP
- **Governance**: CRITICO — auth is the security perimeter; changes affect identity and tenant isolation
