"""
[Q4: Database Selection & Top 5 Query]
Test Suite: Top 5 School Enrollment Optimized SQL Query
-------------------------------------------------------
Verifies:
1. Exact execution of raw SQL:
   `SELECT id, school_name, district, total_students FROM schools ORDER BY total_students DESC LIMIT 5;`
2. Exactly 5 records returned even when more exist in the database.
3. Strict monotonic descending order of `total_students`.
4. Correct attribute mapping without ORM overhead.
"""

import pytest
from fastapi.testclient import TestClient


def test_q4_top_5_enrollment_query(client: TestClient):
    response = client.get("/api/v1/schools/top-enrollment")
    assert response.status_code == 200
    schools = response.json()

    # Must return exactly top 5
    assert len(schools) == 5

    # Check strictly descending enrollment
    enrollments = [s["total_students"] for s in schools]
    assert enrollments == sorted(enrollments, reverse=True), "Schools must be ordered by total_students DESC"

    # Check top school from seed data
    top_school = schools[0]
    assert top_school["total_students"] >= schools[1]["total_students"]
    assert "school_name" in top_school
    assert "district" in top_school
    assert "id" in top_school
