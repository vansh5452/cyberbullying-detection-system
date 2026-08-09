"""
Lightweight in-memory rate limiter (fixed 60-second window, per client IP).

This intentionally does NOT pull in a new dependency (e.g. slowapi/redis) -
the project is a single-process Class 12 deployment, so a small in-memory
counter is enough to make RATE_LIMIT_PER_MINUTE (app/core/config.py) actually
mean something, instead of being a config value nothing reads.

Not distributed-safe: if this API is ever run as multiple worker processes
or behind multiple instances, each process/instance gets its own counter,
so the effective limit becomes RATE_LIMIT_PER_MINUTE * (process count). Fine
for a single-worker deployment; swap for a shared store (e.g. Redis) if you
scale beyond that.
"""
import threading
import time
from typing import Dict, Tuple

from app.core.config import settings

_lock = threading.Lock()
# client_ip -> (window_start_epoch_seconds, request_count_in_window)
_buckets: Dict[str, Tuple[float, int]] = {}

WINDOW_SECONDS = 60


def is_allowed(client_ip: str) -> bool:
    """Returns False once client_ip exceeds RATE_LIMIT_PER_MINUTE requests
    within the current 60-second window."""
    limit = settings.RATE_LIMIT_PER_MINUTE
    if limit <= 0:
        return True  # 0 or negative disables limiting entirely

    now = time.time()
    with _lock:
        window_start, count = _buckets.get(client_ip, (now, 0))
        if now - window_start >= WINDOW_SECONDS:
            # window expired, start a fresh one
            _buckets[client_ip] = (now, 1)
            return True
        if count >= limit:
            return False
        _buckets[client_ip] = (window_start, count + 1)
        return True


def _prune_stale(max_age_seconds: int = 600) -> None:
    """Housekeeping so _buckets doesn't grow forever across many distinct
    client IPs. Called opportunistically from the middleware."""
    now = time.time()
    with _lock:
        stale = [ip for ip, (start, _) in _buckets.items() if now - start >= max_age_seconds]
        for ip in stale:
            _buckets.pop(ip, None)
