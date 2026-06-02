import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")
os.environ.setdefault("SECRET_KEY", "abcd1234abcd1234abcd1234abcd1234")
os.environ.setdefault("ENCRYPTION_KEY", "abcd1234abcd1234abcd1234abcd1234")

import time

import pytest

from app.core.rate_limiter import RateLimiter


class TestRateLimiter:
    async def test_under_limit_allows_request(self):
        limiter = RateLimiter()
        result = await limiter.check("test:key", max_requests=3, window_seconds=60)
        assert result is True

    async def test_exceeding_limit_blocks(self):
        limiter = RateLimiter()
        key = "test:block"
        for _ in range(3):
            await limiter.check(key, max_requests=3, window_seconds=60)
        result = await limiter.check(key, max_requests=3, window_seconds=60)
        assert result is False

    async def test_window_expiration_resets_counter(self):
        limiter = RateLimiter()
        key = "test:window"
        for _ in range(3):
            await limiter.check(key, max_requests=3, window_seconds=1)
        result = await limiter.check(key, max_requests=3, window_seconds=1)
        assert result is False
        time.sleep(1.1)
        result = await limiter.check(key, max_requests=3, window_seconds=1)
        assert result is True

    async def test_different_keys_tracked_separately(self):
        limiter = RateLimiter()
        for _ in range(3):
            await limiter.check("key:a", max_requests=3, window_seconds=60)
        result_a = await limiter.check("key:a", max_requests=3, window_seconds=60)
        assert result_a is False
        result_b = await limiter.check("key:b", max_requests=3, window_seconds=60)
        assert result_b is True
