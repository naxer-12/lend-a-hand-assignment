"""
[Q1: API Development & Error Handling]
Test Suite: Student Registration Validation & RFC 7807 Problem Details
----------------------------------------------------------------------
Verifies:
1. Valid student registration produces HTTP 201 Created.
2. Invalid name regex produces HTTP 422 with RFC 7807 problem details schema.
3. Invalid 64-char hex Aadhaar hash produces HTTP 422 with RFC 7807 details.
4. Non-positive family income produces HTTP 422 with RFC 7807 details.
5. Invalid district outside Gujarat's 33 districts produces HTTP 422.
6. Non-existent school_id produces HTTP 404 with RFC 7807 details.
7. Duplicate Aadhaar hash produces HTTP 409 Conflict with RFC 7807 details.
"""

import pytest
from fastapi.testclient import TestClient


def test_q1_register_student_success(client: TestClient):
    payload = {
        "first_name": "Kavya",
        "last_name": "Trivedi",
        "aadhaar_hash": "a" * 64,
        "aadhaar_last_four": "7788",
        "family_income": 240000.0,
        "district": "Ahmedabad",
        "school_id": 1,
        "attendance_percentage": 91.5,
        "marks_percentage": 84.0,
        "category": "GENERAL"
    }
    response = client.post("/api/v1/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Kavya"
    assert data["last_name"] == "Trivedi"
    assert data["district"] == "Ahmedabad"
    assert data["aadhaar_masked"] == "XXXX-XXXX-7788"


def test_q1_invalid_name_rfc7807_error(client: TestClient):
    payload = {
        "first_name": "Invalid<script>123",
        "last_name": "Patel",
        "aadhaar_hash": "b" * 64,
        "family_income": 120000.0,
        "district": "Gandhinagar",
        "school_id": 1
    }
    response = client.post("/api/v1/students", json=payload)
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"

    problem = response.json()
    assert problem["type"] == "https://evidya.gujarat.gov.in/errors/validation-error"
    assert problem["title"] == "Request Validation Failed"
    assert problem["status"] == 422
    assert "invalid_params" in problem
    assert any("first_name" in p["name"] for p in problem["invalid_params"])


def test_q1_invalid_aadhaar_hash_rfc7807_error(client: TestClient):
    payload = {
        "first_name": "Dev",
        "last_name": "Vyas",
        "aadhaar_hash": "short_hash_not_64_chars",
        "family_income": 120000.0,
        "district": "Gandhinagar",
        "school_id": 1
    }
    response = client.post("/api/v1/students", json=payload)
    assert response.status_code == 422
    problem = response.json()
    assert any("aadhaar_hash" in p["name"] for p in problem["invalid_params"])


def test_q1_negative_family_income_rfc7807_error(client: TestClient):
    payload = {
        "first_name": "Harsh",
        "last_name": "Shah",
        "aadhaar_hash": "c" * 64,
        "family_income": -5000.0,
        "district": "Gandhinagar",
        "school_id": 1
    }
    response = client.post("/api/v1/students", json=payload)
    assert response.status_code == 422
    problem = response.json()
    assert any("family_income" in p["name"] for p in problem["invalid_params"])


def test_q1_invalid_district_rfc7807_error(client: TestClient):
    payload = {
        "first_name": "Pranav",
        "last_name": "Desai",
        "aadhaar_hash": "d" * 64,
        "family_income": 150000.0,
        "district": "NonExistentDistrictSomewhereInSpace",
        "school_id": 1
    }
    response = client.post("/api/v1/students", json=payload)
    assert response.status_code == 422
    problem = response.json()
    assert any("district" in p["name"] for p in problem["invalid_params"])


def test_q1_nonexistent_school_rfc7807_error(client: TestClient):
    payload = {
        "first_name": "Pooja",
        "last_name": "Joshi",
        "aadhaar_hash": "e" * 64,
        "family_income": 150000.0,
        "district": "Gandhinagar",
        "school_id": 999999
    }
    response = client.post("/api/v1/students", json=payload)
    assert response.status_code == 404
    problem = response.json()
    assert problem["status"] == 404
    assert "999999" in problem["detail"]


def test_q1_duplicate_aadhaar_conflict(client: TestClient):
    # Student 1 from conftest already has 64 '1's
    payload = {
        "first_name": "Duplicate",
        "last_name": "Beneficiary",
        "aadhaar_hash": "1" * 64,
        "family_income": 150000.0,
        "district": "Gandhinagar",
        "school_id": 1
    }
    response = client.post("/api/v1/students", json=payload)
    assert response.status_code == 409
    problem = response.json()
    assert problem["status"] == 409
    assert problem["type"] == "https://evidya.gujarat.gov.in/errors/duplicate-aadhaar"
