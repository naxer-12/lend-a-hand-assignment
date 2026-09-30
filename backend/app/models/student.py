"""
[Q1, Q10, Q11: Student Data Model & PII Protection]
Student Entity Definition
-------------------------
Implements secure storage standards for citizen/student PII:
- Raw 12-digit Aadhaar numbers and bank accounts are NEVER stored in plaintext.
- A one-way cryptographic SHA-256 hash (`aadhaar_hash`) allows O(1) deduplication.
- A masked representation (`aadhaar_masked`, e.g. XXXX-XXXX-1234) is retained for display.
- District partitioning enables row-level access control to remediate OWASP BOLA/IDOR (Q10).
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Numeric, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    # Q11: PII Protection - Cryptographic hash for uniqueness; masked string for human UI
    aadhaar_hash = Column(String(64), unique=True, nullable=False, index=True)
    aadhaar_masked = Column(String(20), nullable=False, default="XXXX-XXXX-0000")
    bank_account_masked = Column(String(30), nullable=True, default="XXXXXXXX0000")

    family_income = Column(Numeric(12, 2), nullable=False)

    # Q10: BOLA/IDOR Access Control Boundary - Officers are scoped by district
    district = Column(String(100), nullable=False, index=True)

    # Foreign Key to School
    school_id = Column(Integer, ForeignKey("schools.id", ondelete="RESTRICT"), nullable=False, index=True)

    # Q6: Rule Engine Evaluation Attributes
    attendance_percentage = Column(Float, nullable=False, default=85.0)
    marks_percentage = Column(Float, nullable=False, default=75.0)
    category = Column(String(20), nullable=False, default="GENERAL")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    school = relationship("School", back_populates="students")
    disbursements = relationship("Disbursement", back_populates="student", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_students_district_school", district, school_id),
    )

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, name='{self.first_name} {self.last_name}', district='{self.district}')>"
