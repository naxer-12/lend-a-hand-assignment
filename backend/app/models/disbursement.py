"""
[Q2: Idempotency in State Payment/Scheme APIs]
Disbursement Entity Definition
------------------------------
Tracks direct benefit transfer (DBT) disbursements to students.
Crucially stores `idempotency_key` with a database UNIQUE constraint as the ultimate
safety valve against double-spending if cache eviction occurs during retried payment calls.
Also stores `response_payload` to enable deterministic idempotent replay.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from app.database import Base


class Disbursement(Base):
    __tablename__ = "disbursements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    disbursement_reference = Column(String(64), unique=True, nullable=False, index=True)

    # Q2: Hard unique constraint on Idempotency-Key prevents duplicate state transactions
    idempotency_key = Column(String(128), unique=True, nullable=False, index=True)

    student_id = Column(Integer, ForeignKey("students.id", ondelete="RESTRICT"), nullable=False, index=True)
    scheme_code = Column(String(50), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)

    status = Column(String(30), nullable=False, default="PROCESSING")  # PROCESSING, SUCCESS, FAILED
    payment_gateway_txn_id = Column(String(100), nullable=True)
    executed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Q2: Serialized response cached in DB for replay even across Redis restarts
    response_payload = Column(Text, nullable=True)

    # Relationship
    student = relationship("Student", back_populates="disbursements")

    __table_args__ = (
        Index("idx_disbursements_student_scheme", student_id, scheme_code),
    )

    def __repr__(self) -> str:
        return f"<Disbursement(id={self.id}, ref='{self.disbursement_reference}', key='{self.idempotency_key}', amount={self.amount}, status='{self.status}')>"
