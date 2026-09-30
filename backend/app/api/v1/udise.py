"""
[Q7 (Integration): Central-to-State API Integration (UDISE+ / DigiLocker)]
UDISE+ / DigiLocker Integration Controller
------------------------------------------
Exposes endpoints demonstrating:
1. Integration with Central government services.
2. Token caching with TTL (OAuth2 Client Credentials).
3. Circuit Breaker protection with 2.0-second timeout.
4. Graceful fallback when central services degrade.
"""

from typing import Optional
from fastapi import APIRouter, Query, status
from pydantic import BaseModel
from app.services.udise_client import udise_client

router = APIRouter(prefix="/udise", tags=["UDISE+ Central Integration"])


class CircuitSimulationRequest(BaseModel):
    force_failure: bool = False
    simulate_latency_seconds: float = 0.0


@router.get(
    "/verify/{udise_code}",
    summary="[Q7] Verify School Accreditation & Student Registry via Central UDISE+"
)
async def verify_udise(
    udise_code: str,
    student_id: int = Query(default=1, description="Student ID to cross-verify against central registry")
):
    """
    Executes resilient call to Central UDISE+ with OAuth token caching,
    2-second timeout, circuit breaker guard, and graceful offline fallback.
    """
    return await udise_client.verify_school_and_student(udise_code, student_id)


@router.get(
    "/circuit-status",
    summary="Get current Circuit Breaker state (CLOSED, OPEN, HALF_OPEN)"
)
def get_circuit_status():
    return {
        "circuit_name": udise_client.circuit.name,
        "state": udise_client.circuit.state.value,
        "consecutive_failures": udise_client.circuit.consecutive_failures,
        "failure_threshold": udise_client.circuit.failure_threshold,
        "recovery_timeout_seconds": udise_client.circuit.recovery_timeout,
        "is_token_cached": udise_client._cached_token is not None
    }


@router.post(
    "/circuit/simulate-failure",
    summary="Test harness: Inject latency or failure to trigger Circuit Breaker trip"
)
def configure_circuit_simulation(sim: CircuitSimulationRequest):
    udise_client.force_failure = sim.force_failure
    udise_client.simulate_latency_seconds = sim.simulate_latency_seconds
    return {
        "message": "Circuit simulation parameters updated.",
        "force_failure": udise_client.force_failure,
        "simulate_latency_seconds": udise_client.simulate_latency_seconds,
        "current_circuit_state": udise_client.circuit.state.value
    }
