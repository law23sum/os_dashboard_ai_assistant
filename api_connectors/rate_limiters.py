"""
Simple token bucket rate limiter for async workflows.
"""

from __future__ import annotations

import asyncio
import time


class TokenBucket:
    """Async token bucket rate limiter."""

    def __init__(self, capacity: int, refill_per_sec: int):
        self.capacity = capacity
        self.tokens = float(capacity)
        self.refill_per_sec = refill_per_sec
        self.last = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1) -> None:
        async with self._lock:
            now = time.time()
            elapsed = now - self.last
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_per_sec)
            self.last = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return

            wait_for = (tokens - self.tokens) / self.refill_per_sec

        await asyncio.sleep(wait_for)
        await self.acquire(tokens)



