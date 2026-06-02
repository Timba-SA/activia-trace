## 1. Dependencies and Configuration

- [x] 1.1 Add `pyotp` to `pyproject.toml` dependencies
- [x] 1.2 Add new settings to `core/config.py`: `REFRESH_TOKEN_EXPIRE_DAYS`, `RATE_LIMIT_MAX_REQUESTS`, `RATE_LIMIT_WINDOW_SECONDS`, `RECOVERY_TOKEN_EXPIRE_MINUTES`
- [x] 1.3 Update `.env.example` with new variables and defaults
- [x] 1.4 Create `core/rate_limiter.py` with `RateLimiter` class (in-memory dict + asyncio.Lock)

## 2. Security Primitives

- [x] 2.1 Add `hash_password(password: str) -> str` and `verify_password(password: str, hash: str) -> bool` using Argon2id in `core/security.py`
- [x] 2.2 Add `create_access_token(user_data: dict) -> str` using python-jose in `core/security.py` (claims: sub, tenant_id, roles, exp, iat)
- [x] 2.3 Add `create_temp_token(user_id: uuid.UUID, tenant_id: uuid.UUID) -> str` (5 min TTL, pending_2fa=True)
- [x] 2.4 Add `decode_token(token: str) -> dict` that verifies and decodes JWT in `core/security.py`
- [x] 2.5 Add `generate_refresh_token() -> tuple[str, str]` returning (raw_token, sha256_hash) for opaque refresh tokens

## 3. Models and Migrations

- [x] 3.1 Create `models/usuario.py` with minimal `Usuario` model (id, tenant_id, email, hashed_password, is_active, is_2fa_enabled, totp_secret encrypted, timestamps, soft delete)
- [x] 3.2 Create `models/sesion.py` with `Sesion` model (id, user_id FK, refresh_token_hash, expires_at, is_revoked, created_at)
- [x] 3.3 Create `models/recovery_token.py` with `RecoveryToken` model (id, user_id FK, token_hash, expires_at, used_at)
- [x] 3.4 Generate Alembic migration 002 creating `usuario`, `sesion`, `recovery_token` tables with appropriate indexes (unique email per tenant, index on token_hash)
- [x] 3.5 Create seed data script (backend/scripts/seed_auth.py) with admin@test.com and Argon2id

## 4. Auth Service

- [x] 4.1 Create `services/auth_service.py` with `AuthService` class and methods: `login`, `verify_2fa`, `refresh`, `logout`, `forgot_password`, `reset_password`
- [x] 4.2 Implement `login`: validate credentials (Argon2id), check is_active, check 2FA gate, return tokens or temp_token
- [x] 4.3 Implement `verify_2fa`: verify temp_token JWT, validate TOTP code, issue access + refresh tokens
- [x] 4.4 Implement `refresh`: validate refresh token hash, rotate (revoke old + create new), detect reuse → revoke all
- [x] 4.5 Implement `logout`: revoke current session by refresh token hash
- [x] 4.6 Implement `forgot_password`: generate recovery token, store hash, return raw token
- [x] 4.7 Implement `reset_password`: validate token (hash match, not used, not expired), Argon2id hash new password, mark token used

## 5. 2FA TOTP Service

- [x] 5.1 Create `POST /api/auth/2fa/enroll` endpoint: generate TOTP secret, encrypt with AES-256, return provisioning URI
- [x] 5.2 Create `POST /api/auth/2fa/verify` endpoint: validate TOTP code, enable 2FA for user
- [x] 5.3 Create `POST /api/auth/2fa/disable` endpoint: disable 2FA, clear encrypted secret

## 6. Auth Repositories

- [x] 6.1 Create `repositories/auth_repository.py` with `SessionRepository` (create, find_by_hash, revoke, revoke_all_for_user, mark_reused)
- [x] 6.2 Add `RecoveryTokenRepository` (create, find_by_hash, mark_used)
- [x] 6.3 Add `UserRepository` (find_by_email, find_by_id, update_password, set_2fa_secret, clear_2fa)

## 7. Schemas

- [x] 7.1 Create `schemas/auth.py` with request schemas: `LoginRequest`, `Login2FARequest`, `RefreshRequest`, `ForgotPasswordRequest`, `ResetPasswordRequest`, `Enroll2FARequest`, `Verify2FARequest`
- [x] 7.2 Create response schemas: `TokenResponse`, `LoginResponse`, `TempTokenResponse`, `Enroll2FAResponse`, `RecoveryTokenResponse`
- [x] 7.3 All schemas with `extra='forbid'` per project convention

## 8. API Router

- [x] 8.1 Create `api/v1/routers/auth.py` with endpoints: `POST /login`, `POST /login/2fa`, `POST /refresh`, `POST /logout`, `POST /forgot`, `POST /reset`
- [x] 8.2 Apply `RateLimiter` dependency to login endpoints (5/60s per IP+email)
- [x] 8.3 Register auth router in `main.py`

## 9. Dependencies

- [x] 9.1 Create `CurrentUser` dataclass/class in `schemas/auth.py` or `core/dependencies.py` (id, tenant_id, email, roles, is_active)
- [x] 9.2 Implement `get_current_user` dependency: extract Bearer token, decode JWT, validate user active, return CurrentUser
- [x] 9.3 Ensure `get_current_user` rejects inactive users and ignores identity from request parameters

## 10. Rate Limiting Integration

- [x] 10.1 Wire `RateLimiter` into login endpoint via FastAPI dependency with key = `f"{client_ip}:{email}"`
- [x] 10.2 Return `429 Too Many Requests` with `Retry-After` header when limit exceeded

## 11. Tests

- [x] 11.1 Test login with valid credentials (OK)
- [x] 11.2 Test login with invalid password and nonexistent email (both 401, same error)
- [x] 11.3 Test login for inactive user (401)
- [x] 11.4 Test login with 2FA enabled returns temp_token
- [x] 11.5 Test 2FA login with valid TOTP code
- [x] 11.6 Test 2FA login with invalid TOTP code (401)
- [x] 11.7 Test refresh token rotation (old invalidated, new issued)
- [x] 11.8 Test refresh with revoked token (fraud detection — all sessions revoked)
- [x] 11.9 Test logout revokes session
- [x] 11.10 Test forgot/reset flow: generate token, reset password, use new password to login
- [x] 11.11 Test reset with used token (400)
- [x] 11.12 Test reset with expired token (400)
- [x] 11.13 Test rate limit: 5 attempts OK, 6th fails with 429, wait resets counter
- [x] 11.14 Test get_current_user with valid token returns CurrentUser
- [x] 11.15 Test get_current_user with missing/expired token returns 401
- [x] 11.16 Test identity immutability: request params cannot override token identity
- [x] 11.17 Test 2FA enrollment (enroll → verify → login requires 2FA)
- [x] 11.18 Test 2FA disable (disable → login without 2FA works)
