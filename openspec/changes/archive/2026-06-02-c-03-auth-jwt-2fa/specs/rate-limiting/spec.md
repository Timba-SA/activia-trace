## ADDED Requirements

### Requirement: Rate limiting on login endpoint

The system SHALL limit login attempts to a configurable maximum per IP+email combination within a configurable time window. The default SHALL be 5 attempts per 60 seconds. When the limit is exceeded, the endpoint SHALL return `429 Too Many Requests` with a `Retry-After` header indicating the wait time in seconds. The rate limiter SHALL be in-memory (dict-based) for the MVP.

#### Scenario: Under the limit

- **WHEN** fewer than 5 login attempts are made from the same IP and email within 60 seconds
- **THEN** all requests SHALL be processed normally

#### Scenario: Exceeding the limit

- **WHEN** the 6th login attempt is made from the same IP and email within 60 seconds
- **THEN** the response SHALL be `429 Too Many Requests` with a `Retry-After` header

#### Scenario: Window expiration resets the counter

- **WHEN** 60 seconds have passed since the first login attempt from an IP+email pair
- **THEN** the counter for that pair SHALL reset, allowing new attempts

#### Scenario: Different emails from same IP are tracked separately

- **WHEN** login attempts are made from the same IP but with different emails
- **THEN** each email SHALL have its own independent counter

#### Scenario: Same email from different IPs are tracked separately

- **WHEN** login attempts are made for the same email but from different IPs
- **THEN** each IP SHALL have its own independent counter

### Requirement: Rate limiter module

The system SHALL provide a `RateLimiter` class in a dedicated module (`core/rate_limiter.py`) with a `check(key: str, max_requests: int, window_seconds: int) -> bool` method. The class SHALL be thread-safe (ASGI concurrency safe via `asyncio.Lock` or equivalent). The rate limit configuration (max requests and window) SHALL be configurable via Settings.

#### Scenario: Configurable limits

- **WHEN** `RATE_LIMIT_MAX_REQUESTS` and `RATE_LIMIT_WINDOW_SECONDS` are set in environment
- **THEN** the `RateLimiter` SHALL use those values instead of defaults (5/60)
