"""
[Q4: Database Selection & Top 5 Query]
School Entity Definition
------------------------
Defines the `schools` table with optimized B-tree indices on `total_students`
and `(district, total_students)` to guarantee millisecond latency for state-wide
aggregate analytics queries like top enrollment.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship
from app.database import Base


class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    school_name = Column(String(255), nullable=False)
    district = Column(String(100), nullable=False, index=True)
    total_students = Column(Integer, nullable=False, default=0)
    udise_code = Column(String(50), unique=True, nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    students = relationship("Student", back_populates="school", cascade="all, delete-orphan")

    # Table arguments: Optimized index for Q4 ORDER BY total_students DESC
    __table_args__ = (
        Index("idx_schools_total_students_desc", total_students.desc()),
        Index("idx_schools_district_students", district, total_students.desc()),
    )

    def __repr__(self) -> str:
        return f"<School(id={self.id}, name='{self.school_name}', district='{self.district}', students={self.total_students})>"
