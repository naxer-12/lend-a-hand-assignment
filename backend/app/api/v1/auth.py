"""
Authentication & Token Generation Endpoint
------------------------------------------
Provides standard JWT issuance for development, evaluation, and role simulation.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.api.deps import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


class DemoTokenRequest(BaseModel):
    role: str = "STUDENT"  # STUDENT, DISTRICT_OFFICER, STATE_ADMIN
    user_id: Optional[str] = None
    district: Optional[str] = "Gandhinagar"
    student_id: Optional[int] = 1


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    role: str
    user_id: str
    district: Optional[str] = None
    student_id: Optional[int] = None


@router.post("/token", response_model=TokenResponse)
def generate_demo_token(req: DemoTokenRequest):
    """
    Generates a cryptographically signed JWT token for evaluating role-based workflows:
    - STUDENT (can only access their own student_id record)
    - DISTRICT_OFFICER (can only access students in their assigned district)
    - STATE_ADMIN (full state-wide visibility)
    """
    role = req.role.upper()
    if role not in {"STUDENT", "DISTRICT_OFFICER", "STATE_ADMIN"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be one of: STUDENT, DISTRICT_OFFICER, STATE_ADMIN"
        )

    user_id = req.user_id or f"{role.lower()}_user_01"
    district = req.district if role == "DISTRICT_OFFICER" else (req.district if role == "STUDENT" else None)
    student_id = req.student_id if role == "STUDENT" else None

    token = create_access_token(
        user_id=user_id,
        role=role,
        district=district,
        student_id=student_id
    )

    return TokenResponse(
        access_token=token,
        token_type="Bearer",
        role=role,
        user_id=user_id,
        district=district,
        student_id=student_id
    )
