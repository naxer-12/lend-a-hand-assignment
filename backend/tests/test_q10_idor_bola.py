"""
[Q10: OWASP BOLA / IDOR Remediation]
Test Suite: Broken Object Level Authorization (BOLA) Defense
------------------------------------------------------------
Verifies:
1. Student can inspect ONLY their own registered record (HTTP 200).
2. Student attempting to inspect another student's record is blocked with HTTP 403 Forbidden.
3. District Officer can inspect students belonging to their assigned revenue district (HTTP 200).
4. District Officer attempting cross-district unauthorized inspection is blocked with HTTP 403 Forbidden.
5. State Admin holds authorized universal read permissions across all districts.
6. Missing JWT credentials produce HTTP 401 Unauthorized.
"""

import pytest
from fastapi.testclient import TestClient


def test_q10_student_own_record_permitted(client: TestClient, token_student_1):
    # Student 1 accessing Student 1
    response = client.get(
        "/api/v1/students/1",
        headers={"Authorization": f"Bearer {token_student_1}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["first_name"] == "Aarav"


def test_q10_student_spoofing_another_student_forbidden(client: TestClient, token_student_1):
    # Student 1 attempting to view Student 2 (BOLA / IDOR exploit attempt)
    response = client.get(
        "/api/v1/students/2",
        headers={"Authorization": f"Bearer {token_student_1}"}
    )
    assert response.status_code == 403
    problem = response.json()
    assert problem["status"] == 403
    assert "IDOR/BOLA Protection" in problem["detail"]


def test_q10_district_officer_same_district_permitted(client: TestClient, token_officer_gandhinagar):
    # Student 1 is in Gandhinagar; Officer is in Gandhinagar
    response = client.get(
        "/api/v1/students/1",
        headers={"Authorization": f"Bearer {token_officer_gandhinagar}"}
    )
    assert response.status_code == 200
    assert response.json()["district"] == "Gandhinagar"


def test_q10_district_officer_cross_district_forbidden(client: TestClient, token_officer_gandhinagar):
    # Student 3 is in Surat; Gandhinagar Officer attempts cross-jurisdiction access
    response = client.get(
        "/api/v1/students/3",
        headers={"Authorization": f"Bearer {token_officer_gandhinagar}"}
    )
    assert response.status_code == 403
    problem = response.json()
    assert problem["status"] == 403
    assert "Gandhinagar" in problem["detail"]
    assert "Surat" in problem["detail"]


def test_q10_state_admin_universal_permitted(client: TestClient, token_state_admin):
    # Admin can view Gandhinagar student
    res1 = client.get("/api/v1/students/1", headers={"Authorization": f"Bearer {token_state_admin}"})
    assert res1.status_code == 200

    # Admin can view Surat student
    res2 = client.get("/api/v1/students/3", headers={"Authorization": f"Bearer {token_state_admin}"})
    assert res2.status_code == 200


def test_q10_unauthenticated_request_rejected(client: TestClient):
    response = client.get("/api/v1/students/1")
    assert response.status_code == 401
