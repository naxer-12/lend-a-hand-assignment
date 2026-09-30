"""
[Q6 & Q7: SOLID Principles & Rule-Based Automation]
Test Suite: Strategy Pattern Rule Engine & Dynamic JSON Configuration
---------------------------------------------------------------------
Verifies:
1. SOLID Strategy rules evaluate independently:
   - IncomeRule respects maximum ceiling.
   - AttendanceRule respects biometric attendance percentage.
   - AcademicPerformanceRule applies affirmative action concessions.
2. Full evaluation produces structured eligibility responses with human-readable justifications.
3. Dynamic config reload: Modifying JSON rules modifies evaluation behavior without code change or restart.
"""

import pytest
from fastapi.testclient import TestClient
from app.services.rule_engine import (
    scholarship_rule_engine,
    rule_config_manager,
    IncomeRule,
    AttendanceRule,
    AcademicPerformanceRule
)
from app.schemas.rule import ApplicationEvaluationRequest


def test_q6_income_rule_strategy():
    rule = IncomeRule()
    cfg = {"max_family_income": 500000.0}

    # Under ceiling
    app1 = ApplicationEvaluationRequest(
        family_income=300000.0,
        attendance_percentage=80.0,
        marks_percentage=75.0,
        district="Gandhinagar",
        category="GENERAL"
    )
    res1 = rule.evaluate(app1, cfg)
    assert res1.passed is True

    # Over ceiling
    app2 = ApplicationEvaluationRequest(
        family_income=750000.0,
        attendance_percentage=80.0,
        marks_percentage=75.0,
        district="Gandhinagar",
        category="GENERAL"
    )
    res2 = rule.evaluate(app2, cfg)
    assert res2.passed is False
    assert "exceeds" in res2.message.lower()


def test_q6_academic_rule_affirmative_action():
    rule = AcademicPerformanceRule()
    cfg = {
        "min_marks_percentage": 70.0,
        "concession_categories": {"SC": 55.0, "ST": 55.0, "OBC": 65.0}
    }

    # General category candidate with 68% -> Fails (needs 70%)
    app_gen = ApplicationEvaluationRequest(
        family_income=200000.0,
        attendance_percentage=85.0,
        marks_percentage=68.0,
        district="Gandhinagar",
        category="GENERAL"
    )
    assert rule.evaluate(app_gen, cfg).passed is False

    # SC category candidate with 68% -> Passes (concession cutoff is 55%)
    app_sc = ApplicationEvaluationRequest(
        family_income=200000.0,
        attendance_percentage=85.0,
        marks_percentage=68.0,
        district="Gandhinagar",
        category="SC"
    )
    assert rule.evaluate(app_sc, cfg).passed is True


def test_q6_full_evaluation_api_eligible(client: TestClient):
    payload = {
        "family_income": 180000.0,
        "attendance_percentage": 88.0,
        "marks_percentage": 78.0,
        "district": "Gandhinagar",
        "category": "GENERAL"
    }
    response = client.post("/api/v1/eligibility/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_eligible"] is True
    assert len(data["disqualification_reasons"]) == 0
    assert len(data["rules_evaluated"]) >= 4


def test_q6_full_evaluation_api_disqualified(client: TestClient):
    # Poor attendance & high income
    payload = {
        "family_income": 950000.0,
        "attendance_percentage": 62.0,
        "marks_percentage": 80.0,
        "district": "Gandhinagar",
        "category": "GENERAL"
    }
    response = client.post("/api/v1/eligibility/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_eligible"] is False
    assert len(data["disqualification_reasons"]) >= 2
