## Context

C-02 established the multi-tenant foundation (Tenant model, BaseRepository, AES-256, migrations). `core/security.py` already has AES-256 encryption with a placeholder docstring reserving slots for JWT and Argon2id. `core/dependencies.py` has `get_db` and `get_tenant` (the latter resolves tenant from `X-Tenant-Slug` header). The system has no user model, no auth, and no session concept — every endpoint is open.

C-03 implements the complete auth gateway. This is the security perimeter for the entire system. All subsequent changes (C-04 RBAC through C-24 frontend) depend on it.

## Goals / Non-Goals

**Goals:**
- Minimal `Usuario` model (email, hashed_password, 2fa_secret, is_active, 2fa_enabled) — enough for auth, not for domain (C-07 expands)
- `Sesion` model for refresh token tracking with rotation and revocation
- `RecoveryToken` model for single-use password reset tokens
- JWT access token (15 min) + refresh token (7 days) with rotation (old refresh invalidated on use)
- Claims: `sub` (user_id UUID), `tenant_id` (UUID), `roles` (list[str]), `exp`, `iat`
- Argon2id password hashing/verification in `core/security.py`
- Optional TOTP 2FA per user: enroll secret → verify code → gate session issuance
- `POST /api/auth/login` — validates credentials, if 2FA enabled returns temp_token, else issues session
- `POST /api/auth/login/2fa` — validates TOTP code + temp_token, issues session
- `POST /api/auth/refresh` — rotates refresh token, emits new pair
- `POST /api/auth/logout` — revokes session
- `POST /api/auth/forgot` — generates single-use recovery token by email, short expiry
- `POST /api/auth/reset` — validates recovery token, sets new password
- Rate limiting 5/60s per IP+email on login (in-memory dict)
- Dependency `get_current_user` that extracts and verifies JWT, returns user identity + tenant + roles
- Migration 002: `usuario`, `sesion`, `recovery_token`

**Non-Goals:**
- RBAC, permissions matrix, `require_permission` guard (→ C-04)
- Full User model with PII (DNI, CUIL, CBU) — C-07 expands
- Email sending for forgot password (just the token generation — actual SMTP integration is C-12 or external)
- Database-based rate limiting (in-memory is sufficient for C-03)
- Frontend auth pages (→ C-21)
- Federated auth / SSO (→ Phase 2 per ADR-001)
- Role management (→ C-04)

## Decisions

### D1 — Token format and storage

**Decision**: Access tokens are stateless JWT (RS256 or HS256). Refresh tokens are opaque strings hashed with SHA-256 and stored in the `Sesion` table for revocation. The refresh token itself is a random 32-byte hex string stored as `refresh_token_hash` (SHA-256).

**Why opaque refresh tokens instead of JWT refresh tokens**: A JWT refresh token could be decoded client-side, exposing session metadata. An opaque token cannot. Hash-based storage means the raw token is never persisted — a DB leak does not expose valid tokens.

**Algorithm**: HS256 (HMAC-SHA256) using `SECRET_KEY` from Settings. RS256 would add key management complexity without benefit at this stage.

### D2 — Refresh rotation: invalidate-on-use

**Decision**: When a refresh token is consumed (at `/api/auth/refresh`), the existing `Sesion` record is marked as `is_revoked = True` and a new `Sesion` is created. If a revoked token is reused, the entire family (all sessions for that user) is revoked — this is a security measure against token theft.

**Why**: Refresh rotation with fraud detection is the current OWASP recommendation. If an attacker steals a refresh token and uses it, the legitimate user's next refresh attempt will fail (their token is already invalidated). If the stolen token is reused (detected reuse of revoked token), we revoke all sessions for the user, forcing re-login.

### D3 — 2FA TOTP: gated session issuance

**Decision**: If a user has `is_2fa_enabled = True`, login returns a `temp_token` (short-lived JWT, 5 min, single-use) instead of a session. The client must call `POST /api/auth/login/2fa` with the TOTP code + temp_token to receive the session tokens. The temp_token carries `user_id` and `pending_2fa: True`.

**Why**: This keeps the 2FA gate at the application layer without needing a separate session state store. The temp_token is a stateless JWT, so no DB writes are needed for the pending-2FA state.

**Alternatives considered**: 
- Storing a pending-2FA flag in the Sesion table — rejected because it splits session state between DB and token.
- Using a separate short-lived table — rejected for the same reason; a dedicated temp_token JWT is self-contained.

### D4 — User model: minimal for auth, expand later

**Decision**: The `Usuario` model in C-03 is minimal:
- `id` (UUID, PK, BaseModelMixin)
- `tenant_id` (UUID, FK, BaseModelMixin)
- `email` (unique per tenant)
- `hashed_password` (Argon2id hash)
- `is_active` (bool, default True)
- `is_2fa_enabled` (bool, default False)
- `totp_secret` (encrypted with AES-256 from C-02, nullable)
- Standard timestamps and soft delete from BaseModelMixin

C-07 will expand Usuario with DNI, CUIL, CBU (PII encrypted), name, legajo, etc.

**Why**: C-03 needs a user to authenticate against. Creating a full User model with all PII fields would inflate scope and risk coupling auth to unfinished domain decisions. The minimal model keeps C-03 focused on auth logic.

### D5 — Rate limiting: in-memory sliding window

**Decision**: Use an in-memory dict (`collections.OrderedDict` or a simple dict) keyed by `ip:email` with a list of timestamps. Each login attempt appends the current timestamp and removes entries older than the window. If the count exceeds the limit (5 per 60 seconds), reject with 429.

```python
class RateLimiter:
    _attempts: dict[str, list[float]] = {}
    
    async def check(self, key: str, max_requests: int = 5, window_seconds: int = 60) -> bool:
        now = time.time()
        attempts = self._attempts.get(key, [])
        attempts = [t for t in attempts if now - t < window_seconds]
        if len(attempts) >= max_requests:
            return False
        attempts.append(now)
        self._attempts[key] = attempts
        return True
```

**Alternatives considered**: DB-based rate limiting — rejected because login is a hot path; adding a DB write to every login attempt adds latency and load. A dedicated Redis cache would be ideal but adds infrastructure not yet provisioned. In-memory is acceptable for MVP and will be replaced with Redis in a later optimization.

**Trade-off**: In-memory rate limiting does not persist across app restarts and does not scale across multiple instances. Acceptable for MVP with a single instance. If horizontal scaling is needed, migrate to Redis.

### D6 — JWT creation lives in `core/security.py`

**Decision**: Functions `create_access_token()`, `create_refresh_token()`, `decode_token()` go in `core/security.py`, which already has AES-256 encryption. This keeps all cryptographic operations in one place.

**Why**: Single module for all security primitives. The docstring already reserves this slot for C-03.

### D7 — `get_current_user` replaces current `get_tenant`

**Decision**: The dependency `get_current_user` will:
1. Extract the `Authorization: Bearer <token>` header
2. Decode and verify the JWT
3. Extract `sub` (user_id), `tenant_id`, `roles` from claims
4. Read the `Usuario` from DB (or return a lightweight object with id, tenant_id, roles)
5. Inject into request as `CurrentUser` dataclass/Pydantic model

`get_tenant` from C-02 still works for endpoints that don't need authentication (none in the current system, but kept for backward compatibility). New endpoints should use `get_current_user` which includes tenant resolution.

```python
class CurrentUser:
    id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    roles: list[str]
    is_active: bool
```

### D8 — Single-use recovery token

**Decision**: `RecoveryToken` model: `id` (UUID PK), `user_id` (FK → Usuario), `token_hash` (SHA-256 of the raw token), `expires_at` (timestamp), `used_at` (nullable timestamp). The raw token returned to the client is a random 32-byte hex string. Only the hash is stored.

**Why**: Same rationale as refresh tokens — the raw token is the secret, only its hash is stored. The `used_at` field ensures single-use.

### D9 — Migrations in a single change

**Decision**: One migration (`002_auth`) creates all three tables: `usuario`, `sesion`, `recovery_token`.

**Why**: They are all part of the auth domain and are created together. Splitting them into separate migrations would create an intermediate state where auth is partially functional.

### D10 — Roles in JWT claims as list of strings

**Decision**: The JWT includes a `roles` claim as `list[str]` containing role identifiers (e.g., `["admin"]`, `["profesor", "coordinador"]`). These are resolved from the user's role assignments.

**Why**: While full RBAC (C-04) will implement a role-permission matrix, C-03 needs roles for the `get_current_user` dependency so C-04 can build the permission guard on top. The roles list in the JWT allows C-04 `require_permission` to resolve permissions server-side without an additional DB query for the role set.

**Note**: Permissions are NOT stored in the JWT. Only role identifiers. Permissions are resolved server-side from the role-permission matrix (C-04).

## Risks / Trade-offs

- **In-memory rate limiter resets on restart** → Acceptable for MVP. Documented in D5. Replace with Redis when scaling.
- **Minimal User model creates a data migration path to C-07** → C-07 will add columns (name, DNI, CUIL, CBU) via a new migration. The existing User records from C-03 seed data will get NULL values for new PII fields. Acceptable trade-off.
- **Roles in JWT may become stale** → Roles change infrequently and JWT is short-lived (15 min). On refresh, the new access token re-reads roles from DB. Acceptable for MVP.
- **no email sending for forgot/reset** → C-03 generates the token and stores it. The actual email dispatch depends on the communication module (C-12). For MVP, the token is returned in the API response (for testing) and should be sent via email in production.
- **Temp token for 2FA is single-use** → If the temp_token expires (5 min) or is used, the user must re-authenticate with email+password. This prevents replay attacks.

## Migration Plan

1. Add `pyotp` to pyproject.toml dependencies
2. Add new settings to `core/config.py`: `REFRESH_TOKEN_EXPIRE_DAYS`, `RATE_LIMIT_MAX_REQUESTS`, `RATE_LIMIT_WINDOW_SECONDS`, `RECOVERY_TOKEN_EXPIRE_MINUTES`
3. Add JWT and Argon2id functions to `core/security.py`
4. Create `models/usuario.py`, `models/sesion.py`, `models/recovery_token.py`
5. Create `schemas/auth.py` (LoginRequest, LoginResponse, TokenResponse, etc.)
6. Create `services/auth_service.py` (AuthService with login, refresh, logout, 2fa, recovery)
7. Create `repositories/auth_repository.py` (SessionRepository, RecoveryTokenRepository)
8. Update `core/dependencies.py` — add `get_current_user`
9. Create `api/v1/routers/auth.py` with all auth endpoints
10. Add rate limiter module `core/rate_limiter.py`
11. Generate migration 002 via Alembic
12. Write tests
13. Update `.env.example` with new variables

**Rollback**: `alembic downgrade -1` reverts the migration. Remove auth routes from `main.py`.

## Open Questions

- **Email delivery for forgot password**: C-03 generates the recovery token and stores it. The email dispatch is deferred to when the communication module exists. Should C-03 include a stub/mock email service that logs to console? Decision: Yes — a simple `console_email_service` that logs the token for development/testing.
- **Password policy**: Minimum length? Complexity? Decision: Minimum 8 characters enforced via Pydantic schema validation. No complexity requirements for MVP.
