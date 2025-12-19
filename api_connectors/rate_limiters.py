"""
Simple token bucket rate limiter for async workflows.

Provides a non-blocking token bucket implementation with configurable
capacity and refill rates for rate-limiting API requests.
"""

from __future__ import annotations

import asyncio
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Raised when rate limit cannot be satisfied within timeout."""
    pass


class TokenBucket:
    """Async token bucket rate limiter with bounded waiting.
    
    This implementation prevents infinite recursion by using a loop
    instead of recursive calls and enforcing a maximum wait time.
    """

    def __init__(
        self, 
        capacity: int, 
        refill_per_sec: float,
        max_wait_seconds: float = 60.0
    ):
        """Initialize the token bucket.
        
        Args:
            capacity: Maximum number of tokens the bucket can hold
            refill_per_sec: Rate at which tokens are added per second
            max_wait_seconds: Maximum time to wait for tokens (prevents infinite waits)
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        if refill_per_sec <= 0:
            raise ValueError("Refill rate must be positive")
        
        self.capacity = capacity
        self.tokens = float(capacity)
        self.refill_per_sec = refill_per_sec
        self.max_wait_seconds = max_wait_seconds
        self.last = time.time()
        self._lock = asyncio.Lock()

    def _refill(self) -> None:
        """Refill tokens based on elapsed time since last check."""
        now = time.time()
        elapsed = now - self.last
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_per_sec)
        self.last = now

    async def acquire(self, tokens: int = 1, timeout: Optional[float] = None) -> bool:
        """Acquire tokens from the bucket, waiting if necessary.
        
        Args:
            tokens: Number of tokens to acquire (default: 1)
            timeout: Maximum time to wait in seconds (default: uses max_wait_seconds)
            
        Returns:
            True if tokens were acquired successfully
            
        Raises:
            RateLimitExceeded: If tokens cannot be acquired within timeout
            ValueError: If requesting more tokens than bucket capacity
        """
        if tokens > self.capacity:
            raise ValueError(f"Cannot acquire {tokens} tokens (capacity is {self.capacity})")
        
        if tokens <= 0:
            return True
        
        effective_timeout = timeout if timeout is not None else self.max_wait_seconds
        start_time = time.time()
        
        while True:
            async with self._lock:
                self._refill()
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return True
                
                # Calculate wait time needed
                tokens_needed = tokens - self.tokens
                wait_for = tokens_needed / self.refill_per_sec
                
                # Check if we've exceeded the timeout
                elapsed = time.time() - start_time
                remaining_timeout = effective_timeout - elapsed
                
                if remaining_timeout <= 0:
                    logger.warning(
                        f"Rate limit exceeded: needed {tokens} tokens, "
                        f"only {self.tokens:.2f} available after {elapsed:.2f}s"
                    )
                    raise RateLimitExceeded(
                        f"Could not acquire {tokens} tokens within {effective_timeout}s timeout"
                    )
                
                # Limit wait to remaining timeout
                actual_wait = min(wait_for, remaining_timeout)
            
            # Sleep outside the lock to allow other coroutines to proceed
            await asyncio.sleep(actual_wait)

    async def try_acquire(self, tokens: int = 1) -> bool:
        """Try to acquire tokens without waiting.
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            True if tokens were acquired, False otherwise
        """
        if tokens <= 0:
            return True
        if tokens > self.capacity:
            return False
            
        async with self._lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    @property
    def available_tokens(self) -> float:
        """Return the current number of available tokens (may be stale)."""
        return self.tokens

    def reset(self) -> None:
        """Reset the bucket to full capacity."""
        self.tokens = float(self.capacity)
        self.last = time.time()



