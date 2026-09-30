"""
[Q2: Idempotency in State Payment/Scheme APIs]
Disbursement Request & Response Schemas
---------------------------------------
Handles direct benefit transfer (DBT) payment requests.
The client supplies an `Idempotency-Key` header (enforced at API layer).
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class DisbursementCreate(BaseModel):
    student_id: int = Field(
        ...,
        gt=0,
        description="ID of the eligible student receiving scholarship disbursement",
        examples=[42]
    )
    scheme_code: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Scheme identifier code (e.g. GJ-MYSY-2026)",
        examples=["GJ-MYSY-2026"]
    )
    amount: Decimal = Field(
        ...,
        gt=Decimal("0.0"),
        le=Decimal("250000.0"),
        description="Disbursement amount in INR",
        examples=[25000.00]
    )


class DisbursementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    disbursement_reference: str
    idempotency_key: str
    student_id: int
    scheme_code: str
    amount: float
    status: str
    payment_gateway_txn_id: Optional[str] = None
    executed_at: datetime
    is_idempotent_replay: bool = False
