import time

import asyncio


class RateLimiter:
    _attempts: dict[str, list[float]] = {}
    _lock: asyncio.Lock = asyncio.Lock()

    async def check(
        self, key: str, max_requests: int = 5, window_seconds: int = 60
    ) -> bool:
        now = time.time()
        async with self._lock:
            attempts = self._attempts.get(key, [])
            attempts = [t for t in attempts if now - t < window_seconds]
            if len(attempts) >= max_requests:
                self._attempts[key] = attempts
                return False
            attempts.append(now)
            self._attempts[key] = attempts
            return True
