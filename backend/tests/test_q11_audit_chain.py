"""
[Q11: Audit Trails & PII Protection]
Test Suite: PII Masking, Cryptographic Audit Chaining & Tamper Detection
------------------------------------------------------------------------
Verifies:
1. Citizen PII (Aadhaar & Bank numbers) are returned in masked format (XXXX-XXXX-1234).
2. Administrative views generate immutable audit records with client IP and user agent.
3. Cryptographic chaining links each row to the predecessor's SHA-256 hash.
4. `verify_audit_chain()` verifies intact ledgers.
5. Injected SQL database tampering (unauthorized UPDATE or record mutation) is immediately
   detected and flagged by the mathematical chain verification algorithm.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.services.audit_service import audit_service, mask_aadhaar, mask_bank_account


def test_q11_pii_masking_utility():
    assert mask_aadhaar("123456789012") == "XXXX-XXXX-9012"
    assert mask_bank_account("987654321098") == "XXXXXXXX1098"


def test_q11_view_appends_cryptographic_audit_log(client: TestClient, token_state_admin, db_session: Session):
    # Perform authenticated view of student 1
    response = client.get(
        "/api/v1/students/1",
        headers={"Authorization": f"Bearer {token_state_admin}"}
    )
    assert response.status_code == 200
    student = response.json()
    assert student["aadhaar_masked"] == "XXXX-XXXX-1111"

    # Query audit ledger
    latest_audit = db_session.query(AuditLog).order_by(AuditLog.id.desc()).first()
    assert latest_audit is not None
    assert latest_audit.action == "VIEW_STUDENT_PII"
    assert latest_audit.resource_id == "1"
    assert len(latest_audit.current_record_hash) == 64
    assert len(latest_audit.prev_record_hash) == 64


def test_q11_audit_chain_verification_tamper_free(db_session: Session):
    # Create several audit logs
    audit_service.record_action(
        db=db_session,
        actor_id="admin_01",
        actor_role="STATE_ADMIN",
        action="VIEW_PII",
        resource_type="STUDENT",
        resource_id="1",
        client_ip="10.0.0.1"
    )
    audit_service.record_action(
        db=db_session,
        actor_id="admin_02",
        actor_role="STATE_ADMIN",
        action="UPDATE_STUDENT",
        resource_type="STUDENT",
        resource_id="2",
        client_ip="10.0.0.2"
    )

    verification = audit_service.verify_audit_chain(db_session)
    assert verification["is_valid"] is True
    assert verification["status"] == "VERIFIED_TAMPER_FREE"
    assert verification["total_records"] >= 2


def test_q11_tamper_detection_on_unauthorized_sql_mutation(db_session: Session):
    # Insert 3 records
    for i in range(3):
        audit_service.record_action(
            db=db_session,
            actor_id=f"actor_{i}",
            actor_role="OFFICER",
            action="INSPECT",
            resource_type="STUDENT",
            resource_id=str(i + 1),
            client_ip="127.0.0.1"
        )

    # Confirm initial validity
    assert audit_service.verify_audit_chain(db_session)["is_valid"] is True

    # Simulate Malicious Intrusion: Rogue DB Admin updates record #1 payload without re-hashing
    first_record = db_session.query(AuditLog).order_by(AuditLog.id.asc()).first()
    first_record.actor_id = "MALICIOUS_IMPOSTOR_ACTOR"
    db_session.commit()

    # Run verification - Algorithm must detect cryptographic signature breach!
    tamper_result = audit_service.verify_audit_chain(db_session)
    assert tamper_result["is_valid"] is False
    assert tamper_result["tampered_record_id"] == first_record.id
    assert "RECORD_CONTENT_MUTATED" in tamper_result["status"]
