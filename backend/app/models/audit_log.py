"""
[Q11: Audit Trails & PII Protection]
Immutable Audit Log Entity Definition
-------------------------------------
Records all administrative views and updates of sensitive PII (Aadhaar, income, bank details).
Implements Cryptographic Chaining (blockchain-style tamper detection):
Each row includes `prev_record_hash` which points to the predecessor's `current_record_hash`.
Any modification, deletion, or out-of-order insertion immediately invalidates downstream hashes.
"""

from datetime import datetime, timezone
import hashlib
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Actor Details
    actor_id = Column(String(100), nullable=False, index=True)
    actor_role = Column(String(50), nullable=False)

    # Action & Target Resource
    action = Column(String(100), nullable=False, index=True)  # VIEW_PII, UPDATE_STUDENT, CREATE_DISBURSEMENT
    resource_type = Column(String(50), nullable=False)       # STUDENT, DISBURSEMENT, SCHEME
    resource_id = Column(String(100), nullable=False, index=True)

    # Network Origin for Forensics
    client_ip = Column(String(50), nullable=False)
    user_agent = Column(String(255), nullable=True)

    # Structured details of changes/accessed fields (Aadhaar always masked)
    details = Column(Text, nullable=True)

    # Cryptographic Chain Hashes
    prev_record_hash = Column(String(64), nullable=False)
    current_record_hash = Column(String(64), nullable=False, unique=True, index=True)

    __table_args__ = (
        Index("idx_audit_resource_action", resource_type, resource_id, action),
    )

    @staticmethod
    def calculate_hash(
        prev_hash: str,
        timestamp_str: str,
        actor_id: str,
        actor_role: str,
        action: str,
        resource_type: str,
        resource_id: str,
        client_ip: str,
        details: str = ""
    ) -> str:
        """
        Computes SHA-256 digest over row elements to guarantee immutability.
        """
        raw_payload = f"{prev_hash}|{timestamp_str}|{actor_id}|{actor_role}|{action}|{resource_type}|{resource_id}|{client_ip}|{details or ''}"
        return hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action='{self.action}', actor='{self.actor_id}', hash='{self.current_record_hash[:8]}...')>"
