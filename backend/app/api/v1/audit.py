"""
[Q11: Audit Trails & PII Protection]
Audit Ledger Verification Controller
------------------------------------
Provides cryptographic verification of the portal's audit ledger.
- GET /api/v1/audit/verify: Mathematically verifies the SHA-256 blockchain hash chain.
- GET /api/v1/audit/logs: Lists recent audit events for administrative forensics.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.audit_log import AuditLog
from app.services.audit_service import audit_service
from app.api.deps import get_current_user, CurrentUser

router = APIRouter(prefix="/audit", tags=["Cryptographic Audit Ledger"])


@router.get(
    "/verify",
    summary="[Q11] Cryptographically Verify Audit Log Hash Chain Integrity"
)
def verify_audit_ledger(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    [Q11: Immutable Audit Trail]
    Traverses the audit table sequentially and checks every SHA-256 cryptographic link:
    - Verifies current_record_hash == SHA-256(prev_hash + payload)
    - Verifies prev_record_hash == predecessor.current_record_hash
    Detects any rogue direct SQL UPDATE or DELETE on administrative activity logs.
    """
    if current_user.role != "STATE_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Only STATE_ADMIN can run cryptographic forensic audit audits."
        )

    return audit_service.verify_audit_chain(db)


@router.get(
    "/logs",
    summary="Retrieve recent audit logs with cryptographic hash signatures"
)
def get_recent_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Returns audit trail entries with cryptographic chaining hashes.
    """
    if current_user.role != "STATE_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Audit logs are restricted to STATE_ADMIN."
        )

    logs = db.query(AuditLog).order_by(desc(AuditLog.id)).limit(limit).all()
    return [
        {
            "id": log.id,
            "timestamp": log.timestamp.isoformat(),
            "actor_id": log.actor_id,
            "actor_role": log.actor_role,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "client_ip": log.client_ip,
            "prev_record_hash": log.prev_record_hash,
            "current_record_hash": log.current_record_hash,
            "details": log.details
        }
        for log in logs
    ]
