import time

import pytest

from api_connectors.rate_limiters import TokenBucket


@pytest.mark.asyncio
async def test_token_bucket_waits_when_empty():
    bucket = TokenBucket(capacity=1, refill_per_sec=1)
    await bucket.acquire()  # consume initial token
    start = time.time()
    await bucket.acquire()  # should wait ~1s to refill
    elapsed = time.time() - start
    assert elapsed >= 0.9

