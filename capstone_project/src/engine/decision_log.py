"""
AI Decision Log
Structured, traceable logging of every AI decision.

Each entry records:
  - Which rules triggered
  - What numerical conditions were breached
  - ML model predictions
  - Why the recommendation was selected
  - Supporting indicators

This ensures traceability, which is critical in agentic AI systems.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

from src.engine.rule_engine import RuleResult, RuleEngineOutput
from src.engine.ml_models import MLPredictions


@dataclass
class DecisionEntry:
    """One entry in the AI decision log."""
    decision_id: str
    timestamp: str
    scenario: str

    # Rule engine
    rules_triggered: List[Dict[str, Any]]
    thresholds_breached: List[str]

    # ML predictions
    ml_predictions: Dict[str, Any]

    # Recommendation
    recommendation: str
    reasoning: str
    supporting_indicators: List[str]

    # Agent
    agent_source: str
    expected_kpi_impact: str

    # Logic trace: which rules, ML values, master data led to this recommendation
    logic_trace: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DecisionLog:
    """Full decision log for a scenario analysis run."""
    entries: List[DecisionEntry] = field(default_factory=list)
    run_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    run_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    scenario: str = ""

    # ------------------------------------------------------------------
    # Build helpers
    # ------------------------------------------------------------------
    # Map from rule action keywords to KPI impact descriptions
    _ACTION_KPI_MAP = {
        "DISPATCH_MAINTENANCE": "Line Downtime: +2-8 hrs; On-time Delivery: -5 to -15%",
        "REALLOCATE_LINE": "On-time Delivery: -3 to -10%; Production Efficiency: -15 to -25%",
        "SWITCH_SUPPLIER": "Lead Time: +2-5 days; Inventory Cost: +5 to +10%",
        "INCREASE_SHIFT": "Overtime Cost: +12 to +18%; Worker Availability: +2 to +5%",
        "RAISE_SUPPLY_ALERT": "Inventory Risk: stockout within 2-4 days if not addressed",
    }

    @classmethod
    def from_analysis(
        cls,
        scenario: str,
        rule_output: RuleEngineOutput,
        ml_output: MLPredictions,
        recommendations: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> "DecisionLog":
        """Create a DecisionLog from rule engine + ML + recommendation outputs."""
        log = cls(scenario=scenario)
        context = context or {}

        # Pre-build full rule list (for reference)
        all_rule_dicts = []
        all_breach_strings = []
        for r in rule_output.triggered_rules:
            all_breach_strings.append(f"{r.rule_name}: {r.condition}")
            all_rule_dicts.append({
                "rule": r.rule_name,
                "condition": r.condition,
                "threshold": r.threshold,
                "actual": r.actual_value,
                "action": r.action,
                "severity": r.severity,
            })

        # Build one entry per recommendation — filter rules to only relevant ones
        for rec in recommendations:
            action = rec.get("action", rec.get("recommendation", "N/A"))
            agent = rec.get("source_agent", rec.get("agent", "Orchestrator"))
            reasoning = rec.get("reasoning", rec.get("why", ""))

            # --- KPI impact: prefer orchestrator's value, else derive from action + context ---
            kpi = rec.get("expected_kpi_impact", rec.get("kpi_impact", rec.get("expected_impact", "")))
            if not kpi:
                kpi = cls._derive_kpi_impact(action, rule_output, context)

            # --- Filter rules relevant to THIS recommendation ---
            relevant_rules = []
            relevant_breaches = []
            action_lower = action.lower()
            agent_lower = agent.lower()

            for rd, bs in zip(all_rule_dicts, all_breach_strings):
                rule_action = rd["action"].lower().replace("_", " ")
                rule_name = rd["rule"].lower()
                # Match if rule action appears in recommendation text, or agent name matches
                is_relevant = (
                    rule_action in action_lower
                    or rule_name in action_lower
                    or ("maintenance" in agent_lower and rd["action"] == "DISPATCH_MAINTENANCE")
                    or ("production" in agent_lower and rd["action"] == "REALLOCATE_LINE")
                    or ("inventory" in agent_lower and rd["action"] in ("RAISE_SUPPLY_ALERT", "SWITCH_SUPPLIER"))
                    or ("workforce" in agent_lower and rd["action"] == "INCREASE_SHIFT")
                    or ("supply" in agent_lower and rd["action"] == "SWITCH_SUPPLIER")
                    or ("health" in agent_lower and rd["action"] == "DISPATCH_MAINTENANCE")
                )
                if is_relevant:
                    relevant_rules.append(rd)
                    relevant_breaches.append(bs)

            # If no specific match, include the highest severity rule
            if not relevant_rules and all_rule_dicts:
                severity_order = {"CRITICAL": 3, "HIGH": 2, "MEDIUM": 1, "LOW": 0}
                top_rule = max(all_rule_dicts, key=lambda x: severity_order.get(x["severity"], 0))
                relevant_rules.append(top_rule)
                idx = all_rule_dicts.index(top_rule)
                relevant_breaches.append(all_breach_strings[idx])

            # --- Filter ML predictions to most relevant ---
            entry_ml: Dict[str, Any] = {"models_trained": ml_output.models_trained}
            if "breakdown" in action_lower or "maintenance" in action_lower or "repair" in action_lower or "health" in agent_lower:
                if ml_output.breakdown_predictions:
                    entry_ml["breakdown"] = [
                        {"line": b.line, "probability": b.probability, "risk": b.risk_level}
                        for b in ml_output.breakdown_predictions[:3]
                    ]
            if "delay" in action_lower or "inventory" in agent_lower or "supply" in agent_lower or "reorder" in action_lower:
                if ml_output.delay_prediction:
                    entry_ml["delay"] = {
                        "risk_score": ml_output.delay_prediction.risk_score,
                        "risk_level": ml_output.delay_prediction.risk_level,
                        "factors": ml_output.delay_prediction.factors,
                    }
            if "supplier" in action_lower or "supply" in agent_lower:
                if ml_output.supplier_risks:
                    entry_ml["supplier_risks"] = [
                        {"name": s.supplier_name, "score": s.score, "risk": s.risk_level}
                        for s in ml_output.supplier_risks[:3]
                    ]
            # If nothing matched, include breakdown + delay as default
            if len(entry_ml) == 1:
                if ml_output.breakdown_predictions:
                    entry_ml["breakdown_top"] = {
                        "line": ml_output.breakdown_predictions[0].line,
                        "probability": ml_output.breakdown_predictions[0].probability,
                    }
                if ml_output.delay_prediction:
                    entry_ml["delay_risk"] = ml_output.delay_prediction.risk_score

            # --- Supporting indicators ---
            supporting = []
            for r in rule_output.triggered_rules:
                rule_action_lower = r.action.lower().replace("_", " ")
                if rule_action_lower in action_lower or r.rule_name.lower() in action_lower:
                    supporting.append(f"Rule '{r.rule_name}' fired: {r.condition}")
            if ml_output.breakdown_predictions and ("breakdown" in action_lower or "maintenance" in action_lower or "health" in agent_lower):
                top = ml_output.breakdown_predictions[0]
                supporting.append(f"ML breakdown risk for {top.line}: {top.probability*100:.0f}%")
            if ml_output.delay_prediction and ("delay" in action_lower or "inventory" in agent_lower or "supply" in agent_lower):
                supporting.append(f"ML delay risk: {ml_output.delay_prediction.risk_score*100:.0f}%")
            # Always add at least one indicator
            if not supporting:
                if ml_output.breakdown_predictions:
                    supporting.append(f"ML breakdown risk (top): {ml_output.breakdown_predictions[0].probability*100:.0f}%")
                if ml_output.delay_prediction:
                    supporting.append(f"ML delay risk: {ml_output.delay_prediction.risk_score*100:.0f}%")

            # --- Logic trace: rules, ML values, master data that led to this recommendation ---
            logic_trace = []
            for rd in relevant_rules:
                logic_trace.append(f"Rule '{rd['rule']}': {rd['condition']} (actual={rd.get('actual', 'N/A')}, threshold={rd.get('threshold', 'N/A')})")
            if entry_ml.get("breakdown"):
                for b in entry_ml["breakdown"][:2]:
                    logic_trace.append(f"ML breakdown: {b.get('line', '')} risk {float(b.get('probability', 0))*100:.0f}%")
            if entry_ml.get("delay"):
                d = entry_ml["delay"]
                logic_trace.append(f"ML delay risk: {float(d.get('risk_score', 0))*100:.0f}% ({d.get('risk_level', '')})")
            si = context.get("scenario_impact", {})
            if si.get("mttr_hrs") or si.get("actual_units_lost_during_outage"):
                logic_trace.append(f"Scenario: MTTR {si.get('mttr_hrs', 'N/A')}h, units lost {si.get('actual_units_lost_during_outage', 'N/A')}")

            entry = DecisionEntry(
                decision_id=f"DEC-{log.run_id}-{len(log.entries)+1:02d}",
                timestamp=datetime.now().isoformat(),
                scenario=scenario,
                rules_triggered=relevant_rules,
                thresholds_breached=relevant_breaches,
                ml_predictions=entry_ml,
                recommendation=str(action),
                reasoning=str(reasoning),
                supporting_indicators=supporting,
                agent_source=str(agent),
                expected_kpi_impact=str(kpi),
                logic_trace=logic_trace,
            )
            log.entries.append(entry)

        return log

    @classmethod
    def _derive_kpi_impact(cls, action: str, rule_output: RuleEngineOutput, context: Dict[str, Any] = None) -> str:
        """Derive expected KPI impact from the recommendation action, triggered rules, and context."""
        context = context or {}
        action_lower = action.lower()
        impacts = []

        # Context-aware: use scenario_impact for breakdown/maintenance
        si = context.get("scenario_impact", {})
        mttr_sens = context.get("mttr_sensitivity", {})

        for rule_action, impact_desc in cls._ACTION_KPI_MAP.items():
            action_words = rule_action.lower().replace("_", " ")
            if action_words in action_lower:
                impacts.append(impact_desc)
                break
            for r in rule_output.triggered_rules:
                if r.action == rule_action and r.action.lower().replace("_", " ") in action_lower:
                    impacts.append(impact_desc)
                    break

        if impacts:
            base = "; ".join(impacts)
            # Enrich with context when available
            if si.get("mttr_hrs") and ("maintenance" in action_lower or "breakdown" in action_lower or "repair" in action_lower):
                units_lost = si.get("actual_units_lost_during_outage", "")
                if units_lost:
                    base = f"{base} | Units lost during {si.get('mttr_hrs')}h outage: ~{units_lost}"
            if mttr_sens.get("orders_at_risk") and "realloc" in action_lower:
                base = f"{base} | Orders at risk: {len(mttr_sens['orders_at_risk'])}"
            return base

        # Fallback: match by keywords
        if any(kw in action_lower for kw in ("repair", "maintenance", "breakdown")):
            return cls._derive_with_context(cls._ACTION_KPI_MAP["DISPATCH_MAINTENANCE"], si, mttr_sens)
        if any(kw in action_lower for kw in ("realloc", "production", "line")):
            return cls._derive_with_context(cls._ACTION_KPI_MAP["REALLOCATE_LINE"], si, mttr_sens)
        if any(kw in action_lower for kw in ("supplier", "expedit", "semiconductor")):
            return cls._ACTION_KPI_MAP["SWITCH_SUPPLIER"]
        if any(kw in action_lower for kw in ("overtime", "shift", "workforce", "worker")):
            return cls._ACTION_KPI_MAP["INCREASE_SHIFT"]
        if any(kw in action_lower for kw in ("inventory", "reorder", "stock")):
            return cls._ACTION_KPI_MAP["RAISE_SUPPLY_ALERT"]

        return "Refer to KPI Summary for projected impact"

    @classmethod
    def _derive_with_context(cls, base: str, si: Dict, mttr_sens: Dict) -> str:
        """Append context-specific details to base KPI impact."""
        if si.get("actual_units_lost_during_outage"):
            return f"{base} | Units lost: ~{si['actual_units_lost_during_outage']} during outage"
        if mttr_sens.get("orders_at_risk"):
            return f"{base} | Orders at risk: {len(mttr_sens['orders_at_risk'])}"
        return base

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------
    def to_json(self) -> str:
        return json.dumps(
            {
                "run_id": self.run_id,
                "timestamp": self.run_timestamp,
                "scenario": self.scenario,
                "entries": [e.to_dict() for e in self.entries],
            },
            indent=2,
            default=str,
        )

    @staticmethod
    def _fmt_ml_breakdown(ml: dict) -> str:
        """Format ML breakdown risk as string for Arrow compatibility."""
        if ml.get("breakdown"):
            p = ml["breakdown"][0].get("probability", 0)
            return f"{round(float(p) * 100, 1)}%"
        if ml.get("breakdown_top"):
            p = ml["breakdown_top"].get("probability", 0)
            return f"{round(float(p) * 100, 1)}%"
        return "N/A"

    @staticmethod
    def _fmt_ml_delay(ml: dict) -> str:
        """Format ML delay risk as string for Arrow compatibility."""
        if ml.get("delay"):
            s = ml["delay"].get("risk_score", 0)
            return f"{round(float(s) * 100, 1)}%"
        if "delay_risk" in ml:
            return f"{round(float(ml['delay_risk']) * 100, 1)}%"
        return "N/A"

    def to_dataframe(self):
        import pandas as pd
        rows = []
        for e in self.entries:
            rows.append({
                "Decision ID": e.decision_id,
                "Timestamp": e.timestamp,
                "Scenario": e.scenario,
                "Recommendation": e.recommendation,
                "Agent": e.agent_source,
                "Rules Triggered": len(e.rules_triggered),
                "Thresholds Breached": "; ".join(e.thresholds_breached[:3]),
                "ML Breakdown Risk": DecisionLog._fmt_ml_breakdown(e.ml_predictions),
                "ML Delay Risk": DecisionLog._fmt_ml_delay(e.ml_predictions),
                "KPI Impact": e.expected_kpi_impact,
                "Reasoning": e.reasoning[:120] + "..." if len(e.reasoning) > 120 else e.reasoning,
            })
        return pd.DataFrame(rows)
