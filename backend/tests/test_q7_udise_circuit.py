"""
[Q7 (Integration): Central-to-State API Integration (UDISE+ / DigiLocker)]
Test Suite: OAuth2 Token Caching, Circuit Breaker & Graceful Fallback
--------------------------------------------------------------------
Verifies:
1. OAuth2 Bearer token caching across consecutive requests without redundant grant calls.
2. Normal verification passes through with circuit state CLOSED.
3. Circuit Breaker trips from CLOSED to OPEN upon reaching consecutive failure threshold.
4. Fast-failing behavior in OPEN state without hanging client threads.
5. Graceful fallback payload returned when central service degrades.
"""

import pytest
from app.services.udise_client import (
    UDISEClient,
    CircuitBreaker,
    CircuitState,
    CircuitBreakerOpenException
)


@pytest.mark.asyncio
async def test_q7_oauth2_token_caching():
    client = UDISEClient()
    # First token fetch
    token1 = await client.get_access_token()
    assert token1.startswith("udise_central_bearer_token")

    # Immediate second call must return the exact same cached token
    token2 = await client.get_access_token()
    assert token1 == token2


@pytest.mark.asyncio
async def test_q7_circuit_breaker_normal_closed():
    client = UDISEClient()
    assert client.circuit.state == CircuitState.CLOSED

    res = await client.verify_school_and_student("24060100101", student_id=1)
    assert res["status"] == "SUCCESS"
    assert res["circuit_state"] == "CLOSED"
    assert res["data"]["central_verified"] is True


@pytest.mark.asyncio
async def test_q7_circuit_breaker_trips_to_open_on_failures():
    client = UDISEClient()
    # Configure threshold = 3
    client.circuit.failure_threshold = 3
    client.force_failure = True

    # 1st failure
    res1 = await client.verify_school_and_student("24060100101", 1)
    assert res1["status"] == "FALLBACK_PROVISIONAL"
    assert client.circuit.state == CircuitState.CLOSED

    # 2nd failure
    res2 = await client.verify_school_and_student("24060100101", 1)
    assert client.circuit.state == CircuitState.CLOSED

    # 3rd failure -> Tripped to OPEN
    res3 = await client.verify_school_and_student("24060100101", 1)
    assert client.circuit.state == CircuitState.OPEN
    assert res3["circuit_state"] == "OPEN"

    # 4th call: Must fast-fail immediately without hitting central service
    res4 = await client.verify_school_and_student("24060100101", 1)
    assert res4["status"] == "FALLBACK_PROVISIONAL"
    assert res4["circuit_state"] == "OPEN"
    assert "CIRCUIT_OPEN_FAST_FAIL" in res4["data"]["reason"]
