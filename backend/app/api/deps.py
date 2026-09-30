"""
API Dependencies Module
-----------------------
Provides dependency injection for Database sessions, JWT Authentication,
Current User context, and Role-Based Authorization.
"""

from typing import Optional, Generator
from datetime import datetime, timedelta, timezone
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db

security = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    user_id: str
    role: str  # STUDENT, DISTRICT_OFFICER, STATE_ADMIN
    district: Optional[str] = None
    student_id: Optional[int] = None


def create_access_token(
    user_id: str,
    role: str,
    district: Optional[str] = None,
    student_id: Optional[int] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Helper to generate JWT bearer tokens for users and automated tests."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {
        "sub": user_id,
        "role": role,
        "district": district,
        "student_id": student_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> CurrentUser:
    """
    [Q10: OWASP BOLA / IDOR Remediation]
    Extracts and cryptographically verifies caller identity from JWT Bearer token.
    Throws 401 Unauthorized if missing or invalid.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        role = payload.get("role")
        district = payload.get("district")
        student_id = payload.get("student_id")

        if not user_id or not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Malformed token claims."
            )

        return CurrentUser(
            user_id=user_id,
            role=role,
            district=district,
            student_id=student_id
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session token has expired. Please authenticate again."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature or corrupted token."
        )
