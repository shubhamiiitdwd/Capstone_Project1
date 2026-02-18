"""
Rule Engine / Decision Logic
Deterministic threshold checks and capacity logic.
No LLM dependency – pure Python rules evaluated against plant data.

AI Recommendation Logic (from architecture diagram):
  Demand spike       -> Increase shift
  Chip delay         -> Switch supplier
  Low machine health -> Dispatch maintenance
  Overload           -> Reallocate line
  Low inventory      -> Raise supply alert
  Nothing unusual    -> None
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import pandas as pd


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class RuleResult:
    """One fired (or evaluated) rule."""
    rule_name: str
    triggered: bool
    condition: str          # human-readable condition string
    threshold: float
    actual_value: float
    action: str             # recommended action tag
    severity: str           # LOW / MEDIUM / HIGH / CRITICAL
    details: str = ""       # extra context


@dataclass
class RuleEngineOutput:
    """Aggregated output of the rule engine for one scenario evaluation."""
    all_results: List[RuleResult] = field(default_factory=list)
    triggered_rules: List[RuleResult] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    overall_severity: str = "LOW"

    def summary_text(self) -> str:
        lines = []
        for r in self.triggered_rules:
            lines.append(
                f"[{r.severity}] {r.rule_name}: {r.condition} "
                f"(actual={r.actual_value:.1f}, threshold={r.threshold:.1f}) "
                f"-> {r.action}"
            )
        if not lines:
            lines.append("No rules triggered – all parameters within normal range.")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Thresholds (derived from master data & domain knowledge)
# ---------------------------------------------------------------------------
DEFAULT_THRESHOLDS = {
    "machine_uptime_critical": 75.0,     # below -> DISPATCH_MAINTENANCE
    "machine_uptime_watch": 85.0,        # below -> monitor
    "inventory_critical": 70.0,          # below -> RAISE_SUPPLY_ALERT
    "inventory_watch": 80.0,
    "worker_availability_target": 92.0,  # below -> shift adjustment
    "defect_rate_max": 2.0,              # above -> quality alert
    "demand_spike_sigma": 2.0,           # avg + n*std
}


# ---------------------------------------------------------------------------
# Rule Engine
# ---------------------------------------------------------------------------
class RuleEngine:
    """Evaluates deterministic rules against scenario data + master data."""

    def __init__(self, thresholds: Dict[str, float] = None):
        self.thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def evaluate(
        self,
        scenario_df: pd.DataFrame,
        context: Dict[str, Any],
    ) -> RuleEngineOutput:
        """Run every rule and return aggregated output."""
        results: List[RuleResult] = []

        results += self._check_machine_health(scenario_df, context)
        results += self._check_line_breakdown(context)
        results += self._check_demand_spike(scenario_df, context)
        results += self._check_inventory(scenario_df, context)
        results += self._check_supply_chain(scenario_df, context)
        results += self._check_overload(scenario_df, context)
        results += self._check_workforce(scenario_df, context)

        triggered = [r for r in results if r.triggered]
        actions = list(dict.fromkeys(r.action for r in triggered))  # unique, ordered

        severity_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
        overall = "LOW"
        for r in triggered:
            if severity_order.get(r.severity, 0) > severity_order.get(overall, 0):
                overall = r.severity

        return RuleEngineOutput(
            all_results=results,
            triggered_rules=triggered,
            recommended_actions=actions,
            overall_severity=overall,
        )

    # ------------------------------------------------------------------
    # Individual rules
    # ------------------------------------------------------------------
    def _check_machine_health(
        self, df: pd.DataFrame, ctx: Dict
    ) -> List[RuleResult]:
        results = []
        uptime_by_line = {
            line: float(df[df["Assembly_Line"] == line]["Machine_Uptime_%"].mean())
            for line in df["Assembly_Line"].unique()
        }
        thr = self.thresholds["machine_uptime_critical"]
        for line, uptime in uptime_by_line.items():
            fired = uptime < thr
            results.append(RuleResult(
                rule_name="Low Machine Health",
                triggered=fired,
                condition=f"Machine_Uptime_% for {line} = {uptime:.1f}% < {thr}%",
                threshold=thr,
                actual_value=uptime,
                action="DISPATCH_MAINTENANCE",
                severity="HIGH" if fired else "LOW",
                details=f"Assembly line {line} uptime is {'below' if fired else 'above'} maintenance threshold.",
            ))
        return results

    def _check_line_breakdown(self, ctx: Dict) -> List[RuleResult]:
        """Specific rule for equipment failure events."""
        import re
        results = []
        event_details = ctx.get("event_details", [])
        line_master = ctx.get("line_master", {})

        for ev in event_details:
            desc = str(ev.get("Description", ""))
            is_failure = (
                str(ev.get("Event_Type", "")).lower() == "equipment_failure"
                or "breakdown" in desc.lower()
                or "malfunction" in desc.lower()
            )
            if is_failure:
                # Extract the actual line name from Description (e.g. "HighRange_Line2")
                line_match = re.search(r'((?:HighRange|MedRange)_Line\d+)', desc)
                line_name = line_match.group(1) if line_match else None

                # Fallback to Impact_Areas or Affected_Line columns
                impact_area = ev.get("Impact_Areas", ev.get("Affected_Line", "Unknown"))
                affected_label = line_name if line_name else impact_area

                # Get MTTR from master data for estimated repair
                mttr = line_master.get(line_name, {}).get("mttr_hrs", None) if line_name else None
                repair_str = f"{mttr} hours (MTTR)" if mttr else "Unknown"

                # Get workaround options from scenario_impact context
                si = ctx.get("scenario_impact", {})
                workaround = ", ".join(si.get("workaround_options", [])) if si.get("workaround_options") else "Line_Swap, Manual_Operation"

                results.append(RuleResult(
                    rule_name="Line Breakdown Detected",
                    triggered=True,
                    condition=f"Equipment failure on {affected_label} ({impact_area}) – repair est. {repair_str}",
                    threshold=0,
                    actual_value=0,
                    action="DISPATCH_MAINTENANCE",
                    severity="CRITICAL",
                    details=f"Description: {desc}. Workaround options: {workaround}",
                ))
                # Also fire reallocation
                results.append(RuleResult(
                    rule_name="Line Reallocation Required",
                    triggered=True,
                    condition=f"{affected_label} offline – must redistribute production",
                    threshold=0,
                    actual_value=0,
                    action="REALLOCATE_LINE",
                    severity="HIGH",
                    details=f"Move production to alternate lines while {affected_label} is being repaired. Impact area: {impact_area}.",
                ))
        return results

    def _check_demand_spike(
        self, df: pd.DataFrame, ctx: Dict
    ) -> List[RuleResult]:
        results = []
        avg = float(df["Demand_SUVs"].mean())
        std = float(df["Demand_SUVs"].std())
        peak = float(df["Demand_SUVs"].max())
        sigma = self.thresholds["demand_spike_sigma"]
        thr = avg + sigma * std
        fired = peak > thr
        results.append(RuleResult(
            rule_name="Demand Spike Detection",
            triggered=fired,
            condition=f"Peak demand ({peak:.0f}) {'>' if fired else '<='} threshold ({thr:.0f} = avg+{sigma}*std)",
            threshold=thr,
            actual_value=peak,
            action="INCREASE_SHIFT",
            severity="HIGH" if fired else "LOW",
            details=f"Average demand = {avg:.0f}, std = {std:.0f}",
        ))
        return results

    def _check_inventory(
        self, df: pd.DataFrame, ctx: Dict
    ) -> List[RuleResult]:
        results = []
        thr = self.thresholds["inventory_critical"]
        for line in df["Assembly_Line"].unique():
            level = float(
                df[df["Assembly_Line"] == line]["Inventory_Status_%"].mean()
            )
            fired = level < thr
            results.append(RuleResult(
                rule_name="Low Inventory",
                triggered=fired,
                condition=f"Inventory for {line} = {level:.1f}% < {thr}%",
                threshold=thr,
                actual_value=level,
                action="RAISE_SUPPLY_ALERT",
                severity="HIGH" if fired else "LOW",
                details=f"Assembly line {line} may face stockout risk.",
            ))
        return results

    def _check_supply_chain(
        self, df: pd.DataFrame, ctx: Dict
    ) -> List[RuleResult]:
        results = []
        if "Semiconductor_Availability" in df.columns:
            mode = df["Semiconductor_Availability"].mode().iloc[0]
            shortage_count = int((df["Semiconductor_Availability"] == "Shortage").sum())
            total = len(df)
            fired = mode in ("Shortage", "Critical") or shortage_count > total * 0.3
            results.append(RuleResult(
                rule_name="Semiconductor Supply Risk",
                triggered=fired,
                condition=f"Semiconductor status = {mode} (Shortage in {shortage_count}/{total} records)",
                threshold=0.3,
                actual_value=shortage_count / total if total else 0,
                action="SWITCH_SUPPLIER",
                severity="HIGH" if fired else "LOW",
                details=f"Distribution: {df['Semiconductor_Availability'].value_counts().to_dict()}",
            ))
        return results

    def _check_overload(
        self, df: pd.DataFrame, ctx: Dict
    ) -> List[RuleResult]:
        """Check if production output is being pushed beyond line capacity.
        
        We compare the average production output per line (from simulation)
        against the line's daily capacity from master data, using the OEE
        to determine effective capacity.
        """
        results = []
        line_master = ctx.get("line_master", {})
        if not line_master:
            return results

        # Map simulation line names to master line names
        sim_to_master = {
            "HighRange_1": "HighRange_Line1",
            "HighRange_2": "HighRange_Line2",
            "MediumRange_1": "MedRange_Line1",
            "MediumRange_2": "MedRange_Line2",
            "MediumRange_3": "MedRange_Line3",
        }
        affected_line = ctx.get("scenario_impact", {}).get("affected_line", "")

        for sim_name in df["Assembly_Line"].unique():
            master_name = sim_to_master.get(sim_name, "")
            # Skip the affected line (it is down, no overload check)
            if affected_line and (master_name == affected_line or sim_name == affected_line):
                continue
            line_df = df[df["Assembly_Line"] == sim_name]
            # Use current utilization from master data instead of demand
            cap_info = line_master.get(master_name, {})
            daily_cap = cap_info.get("daily_capacity", 0)
            utilization = cap_info.get("utilization", 80)  # from master: Current_Utilization_%

            if daily_cap > 0:
                fired = utilization > 95
                results.append(RuleResult(
                    rule_name="Line Overload",
                    triggered=fired,
                    condition=f"{sim_name} utilization = {utilization:.0f}% of {daily_cap} units/day capacity",
                    threshold=95.0,
                    actual_value=utilization,
                    action="REALLOCATE_LINE",
                    severity="HIGH" if fired else "LOW",
                    details=f"Daily capacity for {master_name}: {daily_cap} units/day, OEE: {cap_info.get('oee', 0):.0f}%",
                ))
        return results

    def _check_workforce(
        self, df: pd.DataFrame, ctx: Dict
    ) -> List[RuleResult]:
        results = []
        thr = self.thresholds["worker_availability_target"]
        for shift in df["Shift"].unique():
            avail = float(df[df["Shift"] == shift]["Worker_Availability_%"].mean())
            gap = thr - avail
            fired = avail < thr
            results.append(RuleResult(
                rule_name="Workforce Below Target",
                triggered=fired,
                condition=f"Shift {shift} availability = {avail:.1f}% < target {thr}% (gap {gap:.1f}pp)",
                threshold=thr,
                actual_value=avail,
                action="INCREASE_SHIFT",
                severity="MEDIUM" if fired else "LOW",
                details=f"Consider overtime or temporary staff for Shift {shift}.",
            ))
        return results
