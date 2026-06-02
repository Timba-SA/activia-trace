## MODIFIED Requirements

### Requirement: Contrato de variables de entorno base

The config SHALL define the base environment variables plus new auth-related variables: `REFRESH_TOKEN_EXPIRE_DAYS` (default 7), `RATE_LIMIT_MAX_REQUESTS` (default 5), `RATE_LIMIT_WINDOW_SECONDS` (default 60), `RECOVERY_TOKEN_EXPIRE_MINUTES` (default 15).

**Changes from previous version**: Added `REFRESH_TOKEN_EXPIRE_DAYS`, `RATE_LIMIT_MAX_REQUESTS`, `RATE_LIMIT_WINDOW_SECONDS`, `RECOVERY_TOKEN_EXPIRE_MINUTES` as new environment variables with defaults.

#### Scenario: Default refresh token expiration

- **WHEN** no `REFRESH_TOKEN_EXPIRE_DAYS` is provided
- **THEN** `Settings` adopts the default value of 7 days

#### Scenario: Default rate limit parameters

- **WHEN** no `RATE_LIMIT_MAX_REQUESTS` or `RATE_LIMIT_WINDOW_SECONDS` are provided
- **THEN** `Settings` adopts defaults of 5 requests per 60 seconds

#### Scenario: Default recovery token TTL

- **WHEN** no `RECOVERY_TOKEN_EXPIRE_MINUTES` is provided
- **THEN** `Settings` adopts the default value of 15 minutes
