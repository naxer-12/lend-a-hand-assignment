"""
[Q6 & Q7: SOLID Principles & Rule-Based Automation]
Rule Engine Schemas
-------------------
Data contracts for evaluating scholarship eligibility criteria against dynamic rules.
"""

from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ApplicationEvaluationRequest(BaseModel):
    student_id: Optional[int] = None
    family_income: float = Field(..., gt=0, description="Annual family income in INR")
    attendance_percentage: float = Field(..., ge=0, le=100, description="Biometric attendance %")
    marks_percentage: float = Field(..., ge=0, le=100, description="Aggregate marks %")
    category: str = Field(default="GENERAL", description="Social reservation category")
    district: str = Field(..., description="Student district")


class RuleEvaluationItem(BaseModel):
    rule_name: str
    passed: bool
    message: str
    threshold: Optional[str] = None
    actual_value: Optional[str] = None


class ApplicationEvaluationResponse(BaseModel):
    is_eligible: bool
    scheme_name: str
    rules_evaluated: List[RuleEvaluationItem]
    disqualification_reasons: List[str]
    rule_version: str
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
