"""
[Q4: Database Selection & Top 5 Query]
School Schemas
--------------
Represents school entities and high-enrollment leaderboards.
Optimized for zero-overhead serialization of raw SQL tuples.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict


class SchoolRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    school_name: str
    district: str
    total_students: int
    udise_code: Optional[str] = None


class TopSchoolEnrollment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    school_name: str
    district: str
    total_students: int
