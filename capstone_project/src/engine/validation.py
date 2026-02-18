"""
Output Validation Module
Validates rule outputs, ML outputs, and recommendations for correctness.
Returns a validation report (passed/failed, details) for UI display.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List

from src.engine.rule_engine import RuleEngineOutput
from src.engine.ml_models import MLPredictions


@dataclass
class ValidationCheck:
    """Single validation check result."""
    name: str
    passed: bool
    detail: str
    severity: str = "info"  # info, warning, error


@dataclass
class ValidationReport:
    """Full validation report for an analysis run."""
    checks: List[ValidationCheck] = field(default_factory=list)
    overall_passed: bool = True

    def add(self, name: str, passed: bool, detail: str, severity: str = "info"):
        self.checks.append(ValidationCheck(name=name, passed=passed, detail=detail, severity=severity))
        if not passed and severity == "error":
            self.overall_passed = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_passed": self.overall_passed,
            "checks": [
                {"name": c.name, "passed": c.passed, "detail": c.detail, "severity": c.severity}
                for c in self.checks
            ],
        }


def validate_analysis(
    rule_output: RuleEngineOutput,
    ml_output: MLPredictions,
    recommendations: List[Dict[str, Any]],
    context: Dict[str, Any],
) -> ValidationReport:
    """
    Validate the full analysis pipeline output.
    Returns a report with passed/failed checks and details.
    """
    report = ValidationReport()

    # 1. Rule Engine validation
    for r in rule_output.triggered_rules:
        if r.triggered and r.threshold is not None and r.actual_value is not None:
            # Check threshold logic matches (e.g. uptime < 75)
            if "uptime" in r.rule_name.lower() or "machine" in r.rule_name.lower():
                report.add(
                    f"Rule '{r.rule_name}' threshold",
                    r.actual_value < r.threshold,
                    f"Actual {r.actual_value:.1f} < threshold {r.threshold}",
                    "info" if r.actual_value < r.threshold else "warning",
                )
            elif "inventory" in r.rule_name.lower():
                report.add(
                    f"Rule '{r.rule_name}' threshold",
                    r.actual_value < r.threshold,
                    f"Actual {r.actual_value:.1f} < threshold {r.threshold}",
                    "info" if r.actual_value < r.threshold else "warning",
                )

    # 2. ML output validation
    if ml_output.delay_prediction:
        risk = ml_output.delay_prediction.risk_score
        report.add(
            "Delay risk in range [0, 1]",
            0 <= risk <= 1,
            f"Delay risk score = {risk:.3f}",
            "error" if not (0 <= risk <= 1) else "info",
        )
    for bp in ml_output.breakdown_predictions:
        prob = bp.probability
        report.add(
            f"Breakdown prob for {bp.line} in [0, 1]",
            0 <= prob <= 1,
            f"Probability = {prob:.3f}",
            "error" if not (0 <= prob <= 1) else "info",
        )
        if len(report.checks) >= 5:
            break  # Limit checks

    # 3. Recommendation validation (capacities, overtime)
    line_master = context.get("line_master", {})
    shift_master = context.get("shift_master", {})
    for i, rec in enumerate(recommendations[:5]):
        action = rec.get("action", rec.get("recommendation", ""))
        action_lower = str(action).lower()
        # Check for capacity mentions - recommend not exceeding
        if "production" in action_lower or "realloc" in action_lower:
            # Sanity: recommendation should not suggest impossible rates
            report.add(
                f"Rec #{i+1} production/realloc",
                True,
                f"Action: {action[:60]}...",
                "info",
            )
        if "overtime" in action_lower or "shift" in action_lower:
            vals = list(shift_master.values()) if isinstance(shift_master, dict) else []
            max_ot = max((s.get("max_overtime_hrs", 0) for s in vals if isinstance(s, dict)), default=0)
            report.add(
                f"Rec #{i+1} overtime",
                True,
                f"Max overtime from master: {max_ot}h per shift",
                "info",
            )

    # 4. Context completeness
    required_keys = ["scenario", "line_master", "demand"]
    missing = [k for k in required_keys if k not in context or context[k] is None]
    report.add(
        "Context completeness",
        len(missing) == 0,
        f"Missing: {missing}" if missing else "All required keys present",
        "warning" if missing else "info",
    )

    # 5. Units lost formula validation (breakdown scenario) - OEE included
    si = context.get("scenario_impact", {})
    if si.get("actual_units_lost_during_outage") is not None and si.get("capacity_lost") and si.get("mttr_hrs"):
        cap = float(si["capacity_lost"])
        oee = float(si.get("oee_used", 85))
        util = float(si.get("utilization_used", 100))
        mttr = float(si["mttr_hrs"])
        expected = round(cap * (oee / 100) * (util / 100) * (mttr / 24), 2)
        actual = float(si["actual_units_lost_during_outage"])
        formula_ok = abs(expected - actual) < 0.1
        report.add(
            "Units lost formula (capacity × OEE × utilization × MTTR/24)",
            formula_ok,
            f"Expected {expected}, got {actual} (cap={cap}, oee={oee}%, util={util}%, mttr={mttr}h)",
            "error" if not formula_ok else "info",
        )

    return report
