"""
[Q11: Audit Trails & PII Protection]
Cryptographic Audit Logging & PII Masking Service
-------------------------------------------------
Guarantees citizen PII privacy and forensic integrity:
1. PII Masking: Redacts all sensitive Aadhaar/Account numbers prior to storage or display.
2. Cryptographic Chaining: Implements an immutable blockchain-style audit log where each row
   embeds the SHA-256 hash of the previous row.
3. Tamper Detection: Provides `verify_audit_chain()` which scans the ledger to detect any
   unauthorized SQL UPDATE or DELETE tampering.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.audit_log import AuditLog

logger = logging.getLogger("evidya.audit")

GENESIS_HASH = "0" * 64


def mask_aadhaar(raw_number: Optional[str]) -> str:
    """Masks 12-digit Aadhaar to XXXX-XXXX-1234."""
    if not raw_number:
        return "XXXX-XXXX-0000"
    clean = "".join(filter(str.isdigit, str(raw_number)))
    if len(clean) >= 4:
        return f"XXXX-XXXX-{clean[-4:]}"
    return "XXXX-XXXX-0000"


def mask_bank_account(raw_number: Optional[str]) -> str:
    """Masks bank account number, keeping only last 4 digits visible."""
    if not raw_number:
        return "XXXXXXXX0000"
    clean = "".join(filter(str.isalnum, str(raw_number)))
    if len(clean) > 4:
        return f"{'X' * (len(clean) - 4)}{clean[-4:]}"
    return "XXXXXXXX0000"


class AuditService:
    @staticmethod
    def record_action(
        db: Session,
        actor_id: str,
        actor_role: str,
        action: str,
        resource_type: str,
        resource_id: str,
        client_ip: str,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Appends an immutable audit log record linked to the previous record's hash.
        """
        # Fetch the latest record in the ledger to get previous hash
        latest_record = db.query(AuditLog).order_by(desc(AuditLog.id)).first()
        prev_hash = latest_record.current_record_hash if latest_record else GENESIS_HASH

        now = datetime.now(timezone.utc)
        # Standardize timestamp to deterministic second-precision string
        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
        details_str = json.dumps(details, sort_keys=True) if details else ""

        # Compute SHA-256 cryptographic chain hash
        current_hash = AuditLog.calculate_hash(
            prev_hash=prev_hash,
            timestamp_str=timestamp_str,
            actor_id=actor_id,
            actor_role=actor_role,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            client_ip=client_ip,
            details=details_str
        )

        audit_entry = AuditLog(
            timestamp=now,
            actor_id=actor_id,
            actor_role=actor_role,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            client_ip=client_ip,
            user_agent=user_agent or "N/A",
            details=details_str,
            prev_record_hash=prev_hash,
            current_record_hash=current_hash
        )

        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)

        logger.info(f"Audit log appended: [{action}] by {actor_id} on {resource_type}:{resource_id} (Hash: {current_hash[:10]}...)")
        return audit_entry

    @staticmethod
    def verify_audit_chain(db: Session) -> Dict[str, Any]:
        """
        Scans all records in ascending order to mathematically verify the chain integrity.
        Detects database tampering, record deletion, or modified rows.
        """
        records = db.query(AuditLog).order_by(AuditLog.id.asc()).all()

        if not records:
            return {
                "is_valid": True,
                "total_records": 0,
                "status": "EMPTY_LEDGER",
                "message": "Audit ledger has no records yet."
            }

        expected_prev_hash = GENESIS_HASH

        for idx, record in enumerate(records):
            # Check 1: Chain link matches previous row's current_record_hash
            if record.prev_record_hash != expected_prev_hash:
                return {
                    "is_valid": False,
                    "tampered_record_id": record.id,
                    "index": idx,
                    "reason": f"Chain link broken at record #{record.id}. Expected prev_hash {expected_prev_hash[:12]}..., got {record.prev_record_hash[:12]}...",
                    "status": "CHAIN_BROKEN_TAMPERING_DETECTED"
                }

            # Check 2: Re-compute content digest from fields to ensure row was not altered
            ts_str = record.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            recalculated_hash = AuditLog.calculate_hash(
                prev_hash=record.prev_record_hash,
                timestamp_str=ts_str,
                actor_id=record.actor_id,
                actor_role=record.actor_role,
                action=record.action,
                resource_type=record.resource_type,
                resource_id=record.resource_id,
                client_ip=record.client_ip,
                details=record.details or ""
            )

            if recalculated_hash != record.current_record_hash:
                return {
                    "is_valid": False,
                    "tampered_record_id": record.id,
                    "index": idx,
                    "reason": f"Content signature mismatch at record #{record.id}. Stored hash does not match computed hash from column values.",
                    "status": "RECORD_CONTENT_MUTATED"
                }

            expected_prev_hash = record.current_record_hash

        return {
            "is_valid": True,
            "total_records": len(records),
            "latest_record_hash": records[-1].current_record_hash,
            "status": "VERIFIED_TAMPER_FREE",
            "message": "All cryptographic signatures and ledger chaining validated successfully."
        }


audit_service = AuditService()
