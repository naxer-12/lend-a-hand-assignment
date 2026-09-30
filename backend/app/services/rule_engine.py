"""
[Q6 & Q7: SOLID Principles & Rule-Based Automation]
Scholarship Eligibility Rule Engine
-----------------------------------
Implements the Strategy Pattern and adheres to SOLID design principles:
- Single Responsibility: Each rule strategy evaluates exactly one domain constraint.
- Open/Closed: New criteria (e.g. sports quota, disability concession) extend `EligibilityRule`
  without altering the orchestrator.
- Liskov Substitution: All rule strategies are interchangeable through `evaluate()`.
- Interface Segregation: Clean, minimal contract for rule evaluators.
- Dependency Inversion: High-level `ScholarshipRuleEngine` depends on abstract `EligibilityRule`
  interfaces rather than concrete implementations.

Zero-Downtime Rule Updates:
The engine dynamically checks the `scholarship_rules.json` file timestamp. Any policy modification
by state educational authorities takes effect instantly on the next API call without restarting the process.
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.config import settings
from app.schemas.rule import (
    ApplicationEvaluationRequest,
    ApplicationEvaluationResponse,
    RuleEvaluationItem
)

logger = logging.getLogger("evidya.rule_engine")


# --- Strategy Pattern Interface (LSP & ISP) ---
class EligibilityRule(ABC):
    @property
    @abstractmethod
    def rule_key(self) -> str:
        """Unique key mapping to JSON configuration rule block."""
        pass

    @abstractmethod
    def evaluate(self, app_data: ApplicationEvaluationRequest, config: Dict[str, Any]) -> RuleEvaluationItem:
        """
        Evaluates candidate data against rule criteria.
        Returns RuleEvaluationItem indicating pass/fail, human message, and thresholds.
        """
        pass


# --- Concrete Strategy Implementations (SRP) ---
class IncomeRule(EligibilityRule):
    @property
    def rule_key(self) -> str:
        return "income_criterion"

    def evaluate(self, app_data: ApplicationEvaluationRequest, config: Dict[str, Any]) -> RuleEvaluationItem:
        max_income = float(config.get("max_family_income", 600000.0))
        actual = float(app_data.family_income)
        passed = actual <= max_income
        return RuleEvaluationItem(
            rule_name="Income Eligibility",
            passed=passed,
            threshold=f"<= ₹{max_income:,.2f}",
            actual_value=f"₹{actual:,.2f}",
            message="Income within prescribed ceiling." if passed else f"Family income exceeds maximum threshold of ₹{max_income:,.2f}."
        )


class AttendanceRule(EligibilityRule):
    @property
    def rule_key(self) -> str:
        return "attendance_criterion"

    def evaluate(self, app_data: ApplicationEvaluationRequest, config: Dict[str, Any]) -> RuleEvaluationItem:
        min_attendance = float(config.get("min_attendance_percentage", 75.0))
        actual = float(app_data.attendance_percentage)
        passed = actual >= min_attendance
        return RuleEvaluationItem(
            rule_name="Biometric Attendance Requirement",
            passed=passed,
            threshold=f">= {min_attendance}%",
            actual_value=f"{actual}%",
            message="Satisfies biometric attendance threshold." if passed else f"Attendance of {actual}% is below required {min_attendance}%."
        )


class AcademicPerformanceRule(EligibilityRule):
    @property
    def rule_key(self) -> str:
        return "marks_criterion"

    def evaluate(self, app_data: ApplicationEvaluationRequest, config: Dict[str, Any]) -> RuleEvaluationItem:
        base_marks = float(config.get("min_marks_percentage", 70.0))
        category = app_data.category.upper()
        concessions = config.get("concession_categories", {})

        # Apply affirmative action relaxation based on category
        required_marks = concessions.get(category, base_marks)
        actual = float(app_data.marks_percentage)
        passed = actual >= required_marks
        return RuleEvaluationItem(
            rule_name="Academic Performance Threshold",
            passed=passed,
            threshold=f">= {required_marks}% (Category: {category})",
            actual_value=f"{actual}%",
            message="Academic cutoff satisfied." if passed else f"Marks of {actual}% are below cutoff of {required_marks}%."
        )


class DomicileDistrictRule(EligibilityRule):
    @property
    def rule_key(self) -> str:
        return "domicile_criterion"

    def evaluate(self, app_data: ApplicationEvaluationRequest, config: Dict[str, Any]) -> RuleEvaluationItem:
        # Candidate must reside in a registered Gujarat district
        from app.schemas.student import VALID_GUJARAT_DISTRICTS
        passed = app_data.district in VALID_GUJARAT_DISTRICTS
        return RuleEvaluationItem(
            rule_name="Gujarat Domicile & District Verification",
            passed=passed,
            threshold="Valid Gujarat District",
            actual_value=app_data.district,
            message="Bona fide Gujarat institution enrollment verified." if passed else f"District '{app_data.district}' is not recognized."
        )


# --- Rule Configuration Loader & Orchestrator (DIP) ---
class RuleConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self._cache: Dict[str, Any] = {}
        self._last_mtime: float = 0.0
        self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Loads or reloads configuration if file was updated on disk."""
        try:
            current_mtime = os.path.getmtime(self.config_path)
            if current_mtime > self._last_mtime or not self._cache:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
                self._last_mtime = current_mtime
                logger.info(f"Loaded dynamic scholarship rules (Version: {self._cache.get('version')}) from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to read rules config from {self.config_path}: {e}")
            if not self._cache:
                # Fallback defaults
                self._cache = {
                    "version": "fallback-1.0",
                    "scheme_name": "Mukhyamantri Yuva Swavalamban Yojana",
                    "rules": {
                        "income_criterion": {"enabled": True, "max_family_income": 600000.0},
                        "attendance_criterion": {"enabled": True, "min_attendance_percentage": 75.0},
                        "marks_criterion": {"enabled": True, "min_marks_percentage": 70.0},
                        "domicile_criterion": {"enabled": True}
                    }
                }
        return self._cache

    def update_config_in_memory_or_file(self, new_config: Dict[str, Any], write_to_disk: bool = True) -> None:
        """Enables dynamic updates via admin endpoints."""
        self._cache = new_config
        if write_to_disk:
            try:
                with open(self.config_path, "w", encoding="utf-8") as f:
                    json.dump(new_config, f, indent=2)
                self._last_mtime = os.path.getmtime(self.config_path)
            except Exception as e:
                logger.error(f"Failed to persist updated rules to disk: {e}")


class ScholarshipRuleEngine:
    """
    Orchestrates evaluation of an application across all registered strategy rules.
    """
    def __init__(self, config_manager: RuleConfigManager):
        self.config_manager = config_manager
        self.rules: List[EligibilityRule] = []
        self._register_default_strategies()

    def _register_default_strategies(self):
        """Register the standard suite of rules."""
        self.register_rule(IncomeRule())
        self.register_rule(AttendanceRule())
        self.register_rule(AcademicPerformanceRule())
        self.register_rule(DomicileDistrictRule())

    def register_rule(self, rule: EligibilityRule) -> None:
        """OCP Hook: Allows registering custom rule strategies dynamically."""
        self.rules.append(rule)

    def evaluate(self, application: ApplicationEvaluationRequest) -> ApplicationEvaluationResponse:
        config = self.config_manager.load_config()
        rule_configs = config.get("rules", {})
        results: List[RuleEvaluationItem] = []
        disqualifications: List[str] = []

        for rule in self.rules:
            cfg = rule_configs.get(rule.rule_key, {})
            # Check if this rule is enabled in the dynamic config
            if not cfg.get("enabled", True):
                continue

            result = rule.evaluate(application, cfg)
            results.append(result)
            if not result.passed:
                disqualifications.append(result.message)

        is_eligible = len(disqualifications) == 0

        return ApplicationEvaluationResponse(
            is_eligible=is_eligible,
            scheme_name=config.get("scheme_name", "State Scholarship Scheme"),
            rules_evaluated=results,
            disqualification_reasons=disqualifications,
            rule_version=config.get("version", "unknown")
        )


# Global Singleton
rule_config_manager = RuleConfigManager(settings.RULES_CONFIG_PATH)
scholarship_rule_engine = ScholarshipRuleEngine(rule_config_manager)
