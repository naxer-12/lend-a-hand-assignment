"""
[Q6 & Q7: SOLID Principles & Rule-Based Automation]
Eligibility Rule Engine Controller
----------------------------------
Exposes dynamic rule evaluation endpoints:
- POST /api/v1/eligibility/evaluate: Evaluates student application criteria against dynamic rules.
- GET /api/v1/eligibility/rules: Reads the active scholarship rules configuration.
- PUT /api/v1/eligibility/rules: Allows authorized administrators to hot-update criteria
  (income cap, attendance, marks cutoff) with instant zero-downtime propagation.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, status, HTTPException
from app.schemas.rule import (
    ApplicationEvaluationRequest,
    ApplicationEvaluationResponse
)
from app.services.rule_engine import (
    scholarship_rule_engine,
    rule_config_manager
)
from app.api.deps import get_current_user, CurrentUser

router = APIRouter(prefix="/eligibility", tags=["Eligibility Rule Engine"])


@router.post(
    "/evaluate",
    response_model=ApplicationEvaluationResponse,
    status_code=status.HTTP_200_OK,
    summary="[Q6] Evaluate Scholarship Eligibility via Strategy Rule Engine"
)
def evaluate_eligibility(application: ApplicationEvaluationRequest):
    """
    [Q6: Strategy Pattern & Rule Engine Automation]
    Evaluates candidate parameters (income, attendance, marks, category, domicile)
    against dynamically configured state criteria.
    """
    return scholarship_rule_engine.evaluate(application)


@router.get(
    "/rules",
    response_model=Dict[str, Any],
    summary="Retrieve current dynamic eligibility policy configuration"
)
def get_current_rules():
    """
    Retrieves active JSON rules dynamically loaded from disk.
    """
    return rule_config_manager.load_config()


@router.put(
    "/rules",
    response_model=Dict[str, Any],
    summary="Hot-update eligibility rules without server restart"
)
def update_rules(
    new_config: Dict[str, Any],
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Updates the eligibility criteria JSON dynamically on the fly.
    Only STATE_ADMIN role is permitted to modify state education policy.
    """
    if current_user.role != "STATE_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only STATE_ADMIN can modify state scholarship policy rules."
        )

    rule_config_manager.update_config_in_memory_or_file(new_config, write_to_disk=True)
    return {
        "status": "UPDATED",
        "message": "Scholarship eligibility rules updated successfully without server restart.",
        "config": rule_config_manager.load_config()
    }
