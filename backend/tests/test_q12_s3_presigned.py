"""
[Q12: AWS S3 Storage & Security]
Test Suite: S3 Block Public Access & Pre-Signed URLs
----------------------------------------------------
Verifies:
1. S3 Block Public Access configuration enforcement.
2. Short-lived (5-minute / 300-second) Pre-Signed Upload URL generation.
3. Short-lived (5-minute / 300-second) Pre-Signed View URL generation.
4. Rejection of unapproved file extensions (.exe, .sh).
5. Authorization boundary: Student cannot generate upload tokens for another student's account.
"""

import pytest
from fastapi.testclient import TestClient
from app.services.s3_service import s3_service


def test_q12_block_public_access_enforcement():
    status = s3_service.enforce_bucket_public_access_block()
    assert "APPLIED" in status["status"]
    cfg = status["configuration"]
    assert cfg["BlockPublicAcls"] is True
    assert cfg["IgnorePublicAcls"] is True
    assert cfg["BlockPublicPolicy"] is True
    assert cfg["RestrictPublicBuckets"] is True


def test_q12_presigned_upload_url_student_authorized(client: TestClient, token_student_1):
    payload = {
        "student_id": 1,
        "document_type": "INCOME_CERTIFICATE",
        "filename": "income_cert_tehsildar_2026.pdf",
        "content_type": "application/pdf"
    }
    response = client.post(
        "/api/v1/documents/presigned-upload",
        json=payload,
        headers={"Authorization": f"Bearer {token_student_1}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "upload_url" in data
    assert data["method"] == "PUT"
    assert data["expires_in_seconds"] == 300  # Strict 5 minutes per Q12
    assert "X-Amz-Expires=300" in data["upload_url"]


def test_q12_presigned_upload_student_cross_account_forbidden(client: TestClient, token_student_1):
    # Student 1 attempting to generate upload token for Student 2
    payload = {
        "student_id": 2,
        "document_type": "INCOME_CERTIFICATE",
        "filename": "fake_income.pdf"
    }
    response = client.post(
        "/api/v1/documents/presigned-upload",
        json=payload,
        headers={"Authorization": f"Bearer {token_student_1}"}
    )
    assert response.status_code == 403


def test_q12_presigned_upload_invalid_extension_rejected(client: TestClient, token_student_1):
    payload = {
        "student_id": 1,
        "document_type": "INCOME_CERTIFICATE",
        "filename": "malware.exe"
    }
    response = client.post(
        "/api/v1/documents/presigned-upload",
        json=payload,
        headers={"Authorization": f"Bearer {token_student_1}"}
    )
    assert response.status_code == 400
    assert "extension" in response.json()["detail"].lower()


def test_q12_presigned_view_url(client: TestClient, token_state_admin):
    response = client.get(
        "/api/v1/documents/presigned-view?object_key=students/1/INCOME_CERTIFICATE/cert.pdf",
        headers={"Authorization": f"Bearer {token_state_admin}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "view_url" in data
    assert data["expires_in_seconds"] == 300
    assert "X-Amz-Expires=300" in data["view_url"]
