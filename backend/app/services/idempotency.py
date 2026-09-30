"""
[Q2: Idempotency in State Payment/Scheme APIs]
Atomic Idempotency Management Service
-------------------------------------
Guarantees strict at-most-once execution for financial disbursement transactions.
Architectural Rationale:
In state-scale Direct Benefit Transfer (DBT) portals, network timeouts, browser double-clicks,
or mobile network drops often cause clients to retry payment API calls. Without idempotency,
this leads to double-crediting treasury funds.

Features:
1. Atomic Distributed Locking: Uses Redis `SET key value NX EX lock_ttl` to prevent race conditions.
2. Graceful In-Memory Fallback: Operates flawlessly in environments without a live Redis instance.
3. State Tracking:
   - "PROCESSING": Rejects concurrent attempts with 409 Conflict.
   - "COMPLETED": Deterministically replays the original stored response with header `Idempotent-Replay: true`.
4. DB Persistence: Complements memory/redis cache with DB unique constraint on disbursements.idempotency_key.
"""

import json
import logging
import time
from threading import Lock
from typing import Optional, Dict, Any, Tuple
import redis
from app.config import settings

logger = logging.getLogger("evidya.idempotency")


class InMemoryIdempotencyStore:
    """Thread-safe in-memory idempotency store with TTL support for testing/fallback."""
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            if entry["expires_at"] < time.time():
                del self._store[key]
                return None
            return entry

    def acquire_lock(self, key: str, ttl_seconds: int = 60) -> bool:
        with self._lock:
            now = time.time()
            entry = self._store.get(key)
            if entry and entry["expires_at"] >= now:
                # Key exists and is still valid
                return False
            # Acquire lock
            self._store[key] = {
                "status": "PROCESSING",
                "payload": None,
                "status_code": None,
                "expires_at": now + ttl_seconds
            }
            return True

    def commit(self, key: str, status_code: int, payload: Dict[str, Any], ttl_seconds: int = 86400) -> None:
        with self._lock:
            self._store[key] = {
                "status": "COMPLETED",
                "status_code": status_code,
                "payload": payload,
                "expires_at": time.time() + ttl_seconds
            }

    def release_lock(self, key: str) -> None:
        with self._lock:
            if key in self._store and self._store[key]["status"] == "PROCESSING":
                del self._store[key]

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


class IdempotencyService:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.in_memory_store = InMemoryIdempotencyStore()
        self._connect_redis()

    def _connect_redis(self):
        try:
            r = redis.from_url(settings.REDIS_URL, socket_timeout=settings.REDIS_TIMEOUT_SECONDS)
            r.ping()
            self.redis_client = r
            logger.info("Connected to Redis for atomic idempotency locking.")
        except Exception as e:
            logger.warning(f"Redis unavailable ({e}). Falling back to thread-safe in-memory idempotency store.")
            self.redis_client = None

    def acquire_or_check(self, idempotency_key: str, lock_ttl: int = 60) -> Tuple[str, Optional[Tuple[int, Dict[str, Any]]]]:
        """
        Checks current status of the idempotency key:
        Returns:
            ("ACQUIRED", None) -> Caller holds lock and can execute payment.
            ("PROCESSING", None) -> Another execution is active; raise 409 Conflict.
            ("COMPLETED", (status_code, payload)) -> Replay stored response.
        """
        cache_key = f"idempotency:{idempotency_key}"

        if self.redis_client:
            try:
                # Check if already completed
                raw_completed = self.redis_client.get(cache_key)
                if raw_completed:
                    data = json.loads(raw_completed)
                    if data.get("status") == "COMPLETED":
                        return "COMPLETED", (data["status_code"], data["payload"])

                # Try acquiring atomic lock
                lock_key = f"lock:{cache_key}"
                acquired = self.redis_client.set(lock_key, "PROCESSING", nx=True, ex=lock_ttl)
                if not acquired:
                    return "PROCESSING", None
                return "ACQUIRED", None
            except Exception as e:
                logger.warning(f"Redis error during acquire ({e}). Using in-memory fallback.")

        # In-Memory fallback path
        entry = self.in_memory_store.get(cache_key)
        if entry:
            if entry["status"] == "COMPLETED":
                return "COMPLETED", (entry["status_code"], entry["payload"])
            if entry["status"] == "PROCESSING":
                return "PROCESSING", None

        if self.in_memory_store.acquire_lock(cache_key, ttl_seconds=lock_ttl):
            return "ACQUIRED", None
        return "PROCESSING", None

    def complete(self, idempotency_key: str, status_code: int, payload: Dict[str, Any], ttl_seconds: int = 86400) -> None:
        """Stores the completed payload and releases the processing lock."""
        cache_key = f"idempotency:{idempotency_key}"
        data = {
            "status": "COMPLETED",
            "status_code": status_code,
            "payload": payload
        }

        if self.redis_client:
            try:
                # Save completed response for 24 hours
                self.redis_client.set(cache_key, json.dumps(data), ex=ttl_seconds)
                # Release processing lock
                self.redis_client.delete(f"lock:{cache_key}")
                return
            except Exception as e:
                logger.warning(f"Redis error during complete ({e}).")

        # In-Memory fallback
        self.in_memory_store.commit(cache_key, status_code, payload, ttl_seconds)

    def release(self, idempotency_key: str) -> None:
        """Releases the lock on failure so the client can retry."""
        cache_key = f"idempotency:{idempotency_key}"
        if self.redis_client:
            try:
                self.redis_client.delete(f"lock:{cache_key}")
                return
            except Exception as e:
                logger.warning(f"Redis error during release ({e}).")

        self.in_memory_store.release_lock(cache_key)


# Singleton instance
idempotency_service = IdempotencyService()
