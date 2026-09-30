"""
[Q1, Q10, Q11: Student Validation Schemas]
Student Pydantic v2 Models
--------------------------
Strict domain validation for Gujarat e-Vidya student onboarding:
- Enforces regex constraints on names.
- Validates 64-char hex SHA-256 Aadhaar hashes.
- Enforces positive family income limits.
- District validation against Gujarat's 33 administrative revenue districts.
- Outputs masked PII in read responses (Q11).
"""

import re
from typing import Optional
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


VALID_GUJARAT_DISTRICTS = {
    "Ahmedabad", "Amreli", "Anand", "Aravalli", "Banaskantha", "Bharuch",
    "Bhavnagar", "Botad", "Chhota Udaipur", "Dahod", "Dang", "Devbhoomi Dwarka",
    "Gandhinagar", "Gir Somnath", "Jamnagar", "Junagadh", "Kheda", "Kutch",
    "Mahisagar", "Mehsana", "Morbi", "Narmada", "Navsari", "Panchmahal",
    "Patan", "Porbandar", "Rajkot", "Sabarkantha", "Surat", "Surendranagar",
    "Tapi", "Vadodara", "Valsad"
}

NAME_REGEX = re.compile(r"^[A-Za-z\s.'-]+$")
SHA256_REGEX = re.compile(r"^[a-fA-F0-9]{64}$")


class StudentCreate(BaseModel):
    first_name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Student legal first name",
        examples=["Aarav"]
    )
    last_name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Student legal surname",
        examples=["Patel"]
    )
    aadhaar_hash: str = Field(
        ...,
        description="64-character SHA-256 hexadecimal hash of the student's 12-digit Aadhaar UID",
        examples=["a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"]
    )
    aadhaar_last_four: Optional[str] = Field(
        default="1234",
        min_length=4,
        max_length=4,
        description="Last 4 digits of Aadhaar for display masking (XXXX-XXXX-1234)"
    )
    family_income: Decimal = Field(
        ...,
        gt=Decimal("0.0"),
        le=Decimal("10000000.0"),
        description="Annual household gross family income in INR (must be > 0 and <= 1 Cr)",
        examples=[180000.00]
    )
    district: str = Field(
        ...,
        description="Official Gujarat administrative district",
        examples=["Gandhinagar"]
    )
    school_id: int = Field(
        ...,
        gt=0,
        description="Unique identifier of the registered Gujarat school",
        examples=[101]
    )
    attendance_percentage: Optional[float] = Field(
        default=85.0,
        ge=0.0,
        le=100.0,
        description="Current academic year biometric attendance percentage"
    )
    marks_percentage: Optional[float] = Field(
        default=75.0,
        ge=0.0,
        le=100.0,
        description="Preceding academic year aggregate percentage"
    )
    category: Optional[str] = Field(
        default="GENERAL",
        description="Social reservation category (GENERAL, SC, ST, OBC, EWS)"
    )

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        trimmed = value.strip()
        if not NAME_REGEX.match(trimmed):
            raise ValueError("Name can only contain alphabetical characters, spaces, hyphens, and apostrophes.")
        return trimmed.title()

    @field_validator("aadhaar_hash")
    @classmethod
    def validate_aadhaar_hash(cls, value: str) -> str:
        trimmed = value.strip().lower()
        if not SHA256_REGEX.match(trimmed):
            raise ValueError("aadhaar_hash must be a valid 64-character hexadecimal SHA-256 string.")
        return trimmed

    @field_validator("district")
    @classmethod
    def validate_district(cls, value: str) -> str:
        trimmed = value.strip().title()
        matched = next((d for d in VALID_GUJARAT_DISTRICTS if d.lower() == trimmed.lower()), None)
        if not matched:
            valid_list = ", ".join(sorted(VALID_GUJARAT_DISTRICTS)[:8]) + "..."
            raise ValueError(f"District '{value}' is not a valid Gujarat district. Example valid districts: {valid_list}")
        return matched

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: Optional[str]) -> str:
        if not value:
            return "GENERAL"
        allowed = {"GENERAL", "SC", "ST", "OBC", "EWS"}
        upper = value.strip().upper()
        if upper not in allowed:
            raise ValueError(f"Category must be one of {sorted(allowed)}")
        return upper


class StudentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    aadhaar_masked: str
    bank_account_masked: Optional[str] = None
    family_income: float
    district: str
    school_id: int
    attendance_percentage: float
    marks_percentage: float
    category: str
    created_at: datetime
