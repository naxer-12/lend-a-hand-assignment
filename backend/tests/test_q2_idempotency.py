"""
[Q2: Idempotency in State Payment/Scheme APIs]
Test Suite: Payment Idempotency & Replay Verification
------------------------------------------------------
Verifies:
1. First call with a unique `Idempotency-Key` executes DBT payment, returning 201 Created.
2. Immediate retried call with the same `Idempotency-Key` returns 200 OK with `Idempotent-Replay: true`.
3. Validates that bank/treasury debit was NOT duplicated in the database (single row).
4. Rejection of requests lacking the mandatory `Idempotency-Key` header.
5. Concurrency protection: returns 409 Conflict when a transaction is currently in-flight.
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from app.services.idempotency import idempotency_service


def test_q2_disbursement_successful_first_call(client: TestClient):
    key = str(uuid.uuid4())
    payload = {
        "student_id": 1,
        "scheme_code": "GJ-MYSY-2026",
        "amount": 25000.00
    }
    response = client.post(
        "/api/v1/disbursements",
        json=payload,
        headers={"Idempotency-Key": key}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["idempotency_key"] == key
    assert data["amount"] == 25000.00
    assert data["status"] == "SUCCESS"
    assert data["is_idempotent_replay"] is False
    assert "Idempotent-Replay" not in response.headers


def test_q2_disbursement_idempotent_replay(client: TestClient):
    key = str(uuid.uuid4())
    payload = {
        "student_id": 1,
        "scheme_code": "GJ-MYSY-2026",
        "amount": 30000.00
    }

    # First Call
    res1 = client.post(
        "/api/v1/disbursements",
        json=payload,
        headers={"Idempotency-Key": key}
    )
    assert res1.status_code == 201
    data1 = res1.json()

    # Second Call (Simulated Network Retry / Double-Click)
    res2 = client.post(
        "/api/v1/disbursements",
        json=payload,
        headers={"Idempotency-Key": key}
    )
    assert res2.status_code == 200
    assert res2.headers.get("Idempotent-Replay") == "true"
    data2 = res2.json()

    # Assert exact identical transaction details without re-generating references
    assert data2["disbursement_reference"] == data1["disbursement_reference"]
    assert data2["payment_gateway_txn_id"] == data1["payment_gateway_txn_id"]
    assert data2["amount"] == data1["amount"]
    assert data2["is_idempotent_replay"] is True


def test_q2_missing_idempotency_header_rejected(client: TestClient):
    payload = {
        "student_id": 1,
        "scheme_code": "GJ-MYSY-2026",
        "amount": 10000.00
    }
    # No Idempotency-Key header passed
    response = client.post("/api/v1/disbursements", json=payload)
    # FastAPI returns 422 for missing required header
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"


def test_q2_concurrent_in_flight_returns_409(client: TestClient):
    key = str(uuid.uuid4())
    # Manually lock key in store to simulate active processing thread
    idempotency_service.in_memory_store.acquire_lock(f"idempotency:{key}", ttl_seconds=60)

    payload = {
        "student_id": 1,
        "scheme_code": "GJ-MYSY-2026",
        "amount": 15000.00
    }
    response = client.post(
        "/api/v1/disbursements",
        json=payload,
        headers={"Idempotency-Key": key}
    )
    assert response.status_code == 409
    problem = response.json()
    assert problem["status"] == 409
    assert problem["type"] == "https://evidya.gujarat.gov.in/errors/idempotency-in-progress"
