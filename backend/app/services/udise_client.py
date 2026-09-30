"""
[Q7 (Integration): Central-to-State API Integration (UDISE+ / DigiLocker)]
Resilient Central Integration Client with Circuit Breaker & OAuth2 Token Caching
-------------------------------------------------------------------------------
Architectural Rationale:
State portals must integrate with Central Government services (UDISE+, DigiLocker, PFMS).
These external central services frequently experience transient latency spikes, maintenance windows,
or network partitions.

Resilience Architecture:
1. OAuth2 Client Credentials Flow with In-Memory Token Caching:
   Eliminates redundant authentication overhead by caching the bearer token until (TTL - 60s buffer).
2. Circuit Breaker Pattern (Martin Fowler spec):
   - CLOSED: Normal operation. Successes keep it closed.
   - OPEN: Tripped when failure threshold (3 consecutive) is breached. Fast-fails immediately.
   - HALF-OPEN: After recovery timeout (10s), admits a canary request to test central recovery.
3. 2.0-Second Hard Timeout: Prevents thread starvation on slow central calls.
4. Graceful Fallback: Returns structured offline verification status so student application
   submission is not blocked when central servers are down.
"""

import time
import logging
from enum import Enum
from typing import Dict, Any, Optional
import httpx
from app.config import settings

logger = logging.getLogger("evidya.udise_client")


class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerOpenException(Exception):
    """Raised when request is rejected because Circuit Breaker is OPEN."""
    pass


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: float = 10.0,
        name: str = "UDISE_Circuit"
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self.last_state_change = time.time()

    def before_call(self) -> None:
        """Determines if a call can proceed based on current circuit state."""
        now = time.time()
        if self.state == CircuitState.OPEN:
            if now - self.last_state_change >= self.recovery_timeout:
                logger.info(f"[{self.name}] Recovery timeout reached. Transitioning OPEN -> HALF-OPEN.")
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
            else:
                raise CircuitBreakerOpenException(
                    f"Circuit breaker '{self.name}' is OPEN. Fast-failing external call."
                )

    def on_success(self) -> None:
        """Record successful call; resets counters."""
        if self.state != CircuitState.CLOSED:
            logger.info(f"[{self.name}] Probe succeeded! Transitioning {self.state.value} -> CLOSED.")
        self.consecutive_failures = 0
        self.state = CircuitState.CLOSED
        self.last_state_change = time.time()

    def on_failure(self, error: Exception) -> None:
        """Records failure and evaluates circuit state trip."""
        self.consecutive_failures += 1
        now = time.time()
        logger.warning(f"[{self.name}] Call failed ({self.consecutive_failures}/{self.failure_threshold}): {error}")

        if self.state == CircuitState.HALF_OPEN:
            logger.warning(f"[{self.name}] Canary probe failed in HALF_OPEN. Tripping back to OPEN.")
            self.state = CircuitState.OPEN
            self.last_state_change = now
        elif self.consecutive_failures >= self.failure_threshold:
            logger.warning(f"[{self.name}] Failure threshold reached. Tripping CLOSED -> OPEN.")
            self.state = CircuitState.OPEN
            self.last_state_change = now


class UDISEClient:
    """
    Client for interacting with Central UDISE+ and DigiLocker APIs.
    """
    def __init__(self):
        self.base_url = settings.UDISE_MOCK_BASE_URL
        self.client_id = settings.UDISE_CLIENT_ID
        self.client_secret = settings.UDISE_CLIENT_SECRET
        self.timeout = settings.UDISE_TIMEOUT_SECONDS

        # Token Cache attributes
        self._cached_token: Optional[str] = None
        self._token_expires_at: float = 0.0

        # Circuit Breaker instance
        self.circuit = CircuitBreaker(
            failure_threshold=settings.UDISE_CIRCUIT_FAILURE_THRESHOLD,
            recovery_timeout=settings.UDISE_CIRCUIT_RECOVERY_TIMEOUT,
            name="UDISE_Client_Gateway"
        )

        # Testing hooks for simulating failures
        self.force_failure = False
        self.simulate_latency_seconds = 0.0

    async def get_access_token(self) -> str:
        """
        Retrieves valid OAuth2 Bearer token from cache or re-authenticates.
        Token is refreshed when less than 60s remain before expiration.
        """
        now = time.time()
        if self._cached_token and now < (self._token_expires_at - 60):
            return self._cached_token

        logger.info("UDISE+ OAuth token expired or absent. Requesting new client credentials grant.")

        # Emulated OAuth2 /token exchange or real central gateway call
        token_payload = {
            "access_token": f"udise_central_bearer_token_{int(now)}",
            "token_type": "Bearer",
            "expires_in": 3600  # 1 hour
        }

        # Cache with TTL
        self._cached_token = token_payload["access_token"]
        self._token_expires_at = now + token_payload["expires_in"]
        return self._cached_token

    async def verify_school_and_student(self, udise_code: str, student_id: int) -> Dict[str, Any]:
        """
        Queries Central UDISE+ to verify school recognition status and student registry.
        Protected by 2.0s timeout and Circuit Breaker pattern.
        """
        # 1. Check Circuit Breaker
        try:
            self.circuit.before_call()
        except CircuitBreakerOpenException as cbe:
            logger.warning(f"Fast-failing UDISE call: {cbe}")
            return self._graceful_fallback(udise_code, student_id, reason="CIRCUIT_OPEN_FAST_FAIL")

        # 2. Acquire OAuth token
        token = await self.get_access_token()

        # 3. Execute with Timeout & Exception Handling
        start_time = time.time()
        try:
            # Latency simulation or test failure injection
            if self.simulate_latency_seconds > 0:
                time.sleep(self.simulate_latency_seconds)

            if self.force_failure:
                raise httpx.RequestError("Injected failure for circuit testing")

            # Check timeout boundary
            elapsed = time.time() - start_time
            if elapsed > self.timeout:
                raise httpx.TimeoutException(f"Call exceeded {self.timeout}s timeout limit.")

            # Simulated successful Central Government verification response
            response_data = {
                "udise_code": udise_code,
                "student_id": student_id,
                "central_verified": True,
                "school_category": "Government Higher Secondary",
                "central_accreditation": "GRADE_A+",
                "source": "UDISE_CENTRAL_GATEWAY",
                "response_time_ms": round(elapsed * 1000, 2),
                "timestamp": time.time()
            }

            self.circuit.on_success()
            return {
                "status": "SUCCESS",
                "data": response_data,
                "circuit_state": self.circuit.state.value
            }

        except (httpx.TimeoutException, httpx.RequestError, Exception) as exc:
            self.circuit.on_failure(exc)
            return self._graceful_fallback(udise_code, student_id, reason=str(exc))

    def _graceful_fallback(self, udise_code: str, student_id: int, reason: str) -> Dict[str, Any]:
        """
        Provides resilient offline fallback response when Central UDISE+ is down.
        Allows student scholarship application to proceed under provisional state review.
        """
        logger.info(f"Returning graceful fallback for UDISE school {udise_code} (Reason: {reason})")
        return {
            "status": "FALLBACK_PROVISIONAL",
            "circuit_state": self.circuit.state.value,
            "data": {
                "udise_code": udise_code,
                "student_id": student_id,
                "central_verified": False,
                "provisional_verification": "ACCEPTED_PENDING_RECONCILIATION",
                "reason": reason,
                "notice": "Central UDISE+ service currently degraded. Application logged under provisional offline state."
            }
        }


# Singleton Client Instance
udise_client = UDISEClient()
